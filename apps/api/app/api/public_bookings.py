from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.guest import Gender, Guest, IDType
from app.models.hotel import Hotel, HotelStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.models.room_availability import RoomAvailability
from app.schemas.public_booking import (
    PublicBookingCreate,
    PublicBookingResponse,
    PublicPaymentOptionsResponse,
)
from app.services.commission_service import create_commission
from app.services.pricing import calculate_room_price, property_billing_is_configured
from app.services.reservation_pricing import build_daily_rate_breakdown
from app.services.reservation_service import create_reservation, room_is_available
from app.schemas.reservation import ReservationCreate
from app.api.public_booking_otp import is_verified, send_booking_confirmation

router = APIRouter(prefix="/public/bookings", tags=["Public Bookings"])


@router.get("/payment-options", response_model=PublicPaymentOptionsResponse)
def public_payment_options():
    return PublicPaymentOptionsResponse(
        methods=["pay_at_property", "card", "usdt"],
        usdt_wallet_address=settings.usdt_wallet_address,
        usdt_network=settings.usdt_network,
    )


def _ensure_room_inventory(db: Session, room_type: RoomType) -> list[Room]:
    """Reconcile configured room-type inventory with physical Room rows."""
    rooms = db.query(Room).filter(Room.room_type_id == room_type.id).order_by(Room.id).all()
    configured = max(int(room_type.number_of_rooms or 0), 0)
    if configured <= 0:
        return rooms

    while len(rooms) < configured:
        next_number = len(rooms) + 1
        room = Room(
            room_type_id=room_type.id,
            room_number=f"AUTO-{room_type.id}-{next_number}",
            floor=1,
            smoking=bool(room_type.smoking_allowed),
            active=True,
            status=RoomStatus.AVAILABLE,
        )
        db.add(room)
        db.flush()
        rooms.append(room)
    return rooms


def _calendar_pricing_and_capacity(db: Session, room_type: RoomType, hotel: Hotel, check_in: date, check_out: date):
    """Apply owner daily sell-limit, open/close state and rate overrides."""
    rows = {
        r.date: r
        for r in db.query(RoomAvailability).filter(
            RoomAvailability.room_type_id == room_type.id,
            RoomAvailability.date >= check_in,
            RoomAvailability.date < check_out,
        ).all()
    }
    selling_total = Decimal("0")
    base_total = Decimal("0")
    discount_total = Decimal("0")
    tax_total = Decimal("0")
    d = check_in
    while d < check_out:
        row = rows.get(d)
        if row:
            if not row.bookable:
                raise HTTPException(409, f"This room type is closed for sale on {d}")
            rooms_to_sell = int(row.rooms_to_sell)
            rate_base = Decimal(str(row.rate or 0))
        else:
            rooms_to_sell = int(room_type.number_of_rooms or 0)
            rate_base = Decimal(str(room_type.base_price or 0))
        booked = db.query(Reservation.id).join(Room, Reservation.room_id == Room.id).filter(
            Room.room_type_id == room_type.id,
            Reservation.check_in < d + timedelta(days=1),
            Reservation.check_out > d,
            Reservation.status.notin_([ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]),
        ).count()
        if rooms_to_sell <= booked:
            raise HTTPException(409, f"No room of this type is available for {d}")
        pricing = calculate_room_price(rate_base, Decimal(str(room_type.discount_percent or 0)), Decimal(str(hotel.tax_percent or 0)))
        base_total += pricing.base_price
        discount_total += pricing.discount_amount
        selling_total += pricing.selling_price
        tax_total += pricing.tax_amount
        d += timedelta(days=1)
    return base_total, discount_total, selling_total, tax_total


def _daily_rates(db: Session, room_type: RoomType, hotel: Hotel, check_in: date, check_out: date):
    rows = {
        r.date: {"rate": Decimal(str(r.rate or 0)), "bookable": bool(r.bookable)}
        for r in db.query(RoomAvailability).filter(
            RoomAvailability.room_type_id == room_type.id,
            RoomAvailability.date >= check_in,
            RoomAvailability.date < check_out,
        ).all()
    }
    current = check_in
    while current < check_out:
        if current not in rows:
            rows[current] = {"rate": Decimal(str(room_type.base_price or 0)), "bookable": True}
        current += timedelta(days=1)
    return build_daily_rate_breakdown(
        check_in,
        check_out,
        rows,
        Decimal(str(room_type.discount_percent or 0)),
        Decimal(str(hotel.tax_percent or 0)),
    )


@router.post("/", response_model=PublicBookingResponse, status_code=status.HTTP_201_CREATED)
def create_public_booking(payload: PublicBookingCreate, db: Session = Depends(get_db)):
    try:
        if payload.check_out <= payload.check_in:
            raise HTTPException(400, "Check-out date must be after check-in date")
        if not is_verified(payload.email, payload.otp_token):
            raise HTTPException(400, "Please verify your email before completing the booking")
        if payload.payment_method == "usdt" and not settings.usdt_wallet_address:
            raise HTTPException(503, "USDT payment is not configured yet. Please choose another payment method.")
        if payload.payment_method == "card" and not payload.card_last4:
            raise HTTPException(400, "Please complete the card details before continuing")

        room_type = db.query(RoomType).join(Hotel).filter(
            RoomType.id == payload.room_type_id,
            RoomType.status.is_(True),
            Hotel.status == HotelStatus.APPROVED,
        ).first()
        if not room_type:
            raise HTTPException(404, "Approved room type not found")

        hotel = room_type.hotel
        if not property_billing_is_configured(hotel):
            raise HTTPException(409, "Reservation booking is not available for this property until Tax and Commission are configured by StayHub admin.")

        nights = (payload.check_out - payload.check_in).days
        base_total, discount_amount, selling_total, tax_amount = _calendar_pricing_and_capacity(
            db, room_type, hotel, payload.check_in, payload.check_out
        )
        daily_rates = _daily_rates(db, room_type, hotel, payload.check_in, payload.check_out)

        existing_rooms = _ensure_room_inventory(db, room_type)
        available_room = None
        for room in existing_rooms:
            if not room.active or room.status in [RoomStatus.MAINTENANCE, RoomStatus.OUT_OF_ORDER]:
                continue
            if room_is_available(db, room.id, payload.check_in, payload.check_out):
                available_room = room
                break
        if not available_room:
            raise HTTPException(409, "No room of this type is available for the selected dates")

        guest = Guest(
            hotel_id=hotel.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            gender=Gender.OTHER,
            nationality=payload.nationality,
            id_type=IDType.OTHER,
            id_number=f"STAYHUB-{payload.phone[-8:]}-{date.today().strftime('%Y%m%d')}",
            phone=payload.phone,
            email=payload.email,
            address=payload.address,
            city=payload.city or hotel.city,
            country=payload.country,
        )
        db.add(guest)
        db.flush()

        reservation = create_reservation(
            db=db,
            hotel_id=hotel.id,
            reservation=ReservationCreate(
                guest_id=guest.id,
                room_id=available_room.id,
                booking_source="WEBSITE",
                check_in=payload.check_in,
                check_out=payload.check_out,
                adults=payload.adults,
                children=payload.children,
                # Reservation.room_rate is a single legacy field. For a multi-night
                # reservation it must contain the actual nightly average only as a
                # compatibility value; the authoritative nightly prices are in
                # daily_rates and the authoritative room subtotal is selling_total.
                room_rate=(selling_total / Decimal(nights)).quantize(Decimal("0.01")),
                discount=discount_amount,
                tax=tax_amount,
                remarks=f"Customer booking through StayHub public marketplace | Payment: {payload.payment_method}",
            ),
        )

        # Keep the reservation totals authoritative for the complete stay.
        # Do not divide the stay totals again in the reservation detail layer.
        reservation.discount = discount_amount
        reservation.total_amount = selling_total + tax_amount
        reservation.payment_method = payload.payment_method
        reservation.payment_status = "pending"
        reservation.payment_reference = payload.payment_reference
        reservation.card_last4 = payload.card_last4 if payload.payment_method == "card" else None

        commission = create_commission(db, reservation)
        db.commit()
        db.refresh(reservation)
        db.refresh(commission)
        try:
            send_booking_confirmation(payload.email, reservation.confirmation_no, hotel.name, room_type.name, reservation.check_in, reservation.check_out, reservation.total_amount)
        except Exception as exc:
            print(f"[StayHub confirmation email] {exc}")

        return PublicBookingResponse(
            confirmation_no=reservation.confirmation_no,
            reservation_id=reservation.id,
            status=reservation.status.value,
            hotel_id=hotel.id,
            room_type_id=room_type.id,
            room_name=room_type.name,
            check_in=reservation.check_in,
            check_out=reservation.check_out,
            nights=nights,
            base_price=base_total,
            discount_percent=room_type.discount_percent,
            discount_amount=discount_amount,
            selling_price=selling_total,
            tax_percent=hotel.tax_percent,
            tax_amount=tax_amount,
            total_amount=reservation.total_amount,
            daily_rates=daily_rates,
            commission_percent=commission.commission_percent,
            commission_amount=commission.commission_amount,
            owner_amount=commission.owner_amount,
            payment_method=reservation.payment_method,
            payment_status=reservation.payment_status,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        print(f"[StayHub public booking] {type(exc).__name__}: {exc}")
        raise HTTPException(500, f"Booking could not be completed: {exc}") from exc
