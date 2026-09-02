from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.hotel import Hotel
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_commission import ReservationCommission
from app.models.user import User
from app.services.commission_service import sync_commission_status

router = APIRouter(prefix="/admin/reservations", tags=["Admin - Reservations"])


def serialize(reservation, commission=None):
    guest = reservation.guest
    room = reservation.room
    room_type = room.room_type if room else None
    commission = commission or reservation.commission
    owner = reservation.hotel.owner if reservation.hotel else None
    return {
        "id": reservation.id,
        "hotel_id": reservation.hotel_id,
        "hotel_name": reservation.hotel.name if reservation.hotel else None,
        "owner_user_id": owner.id if owner else None,
        "owner_name": owner.full_name if owner else None,
        "owner_email": owner.email if owner else None,
        "guest_id": reservation.guest_id,
        "guest_name": f"{guest.first_name} {guest.last_name}".strip() if guest else None,
        "guest_phone": guest.phone if guest else None,
        "guest_email": guest.email if guest else None,
        "guest_city": guest.city if guest else None,
        "guest_country": guest.country if guest else None,
        "room_id": reservation.room_id,
        "room_number": room.room_number if room else None,
        "room_type_id": room_type.id if room_type else None,
        "room_type_name": room_type.name if room_type else None,
        "confirmation_no": reservation.confirmation_no,
        "booking_source": reservation.booking_source.value,
        "check_in": reservation.check_in,
        "check_out": reservation.check_out,
        "created_at": reservation.created_at,
        "adults": reservation.adults,
        "children": reservation.children,
        "room_rate": reservation.room_rate,
        "discount": reservation.discount,
        "tax": reservation.tax,
        "total_amount": reservation.total_amount,
        "status": reservation.status.value,
        "remarks": reservation.remarks,
        "payment_method": reservation.payment_method,
        "payment_status": reservation.payment_status,
        "payment_reference": reservation.payment_reference,
        "card_last4": reservation.card_last4,
        "commission_percent": commission.commission_percent if commission else None,
        "commission_amount": commission.commission_amount if commission else None,
        "commissionable_amount": commission.commissionable_amount if commission else None,
        "owner_amount": commission.owner_amount if commission else None,
        "commission_status": commission.status if commission else None,
    }


@router.get("/")
def reservations(
    hotel_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(Reservation).order_by(Reservation.id.desc())
    if hotel_id is not None:
        query = query.filter(Reservation.hotel_id == hotel_id)
    if status_filter:
        try:
            query = query.filter(Reservation.status == ReservationStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid reservation status")
    rows = query.limit(500).all()
    result = []
    for item in rows:
        result.append(serialize(item, sync_commission_status(db, item)))
    db.commit()
    return result


@router.get("/daily")
def daily_reservations(
    report_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    rows = (
        db.query(
            Hotel.id.label("hotel_id"), Hotel.name.label("hotel_name"),
            func.count(Reservation.id).label("reservations"),
            func.coalesce(func.sum(Reservation.total_amount), 0).label("revenue"),
            func.coalesce(func.sum(ReservationCommission.commission_amount), 0).label("commission"),
        )
        .join(Reservation, Reservation.hotel_id == Hotel.id)
        .outerjoin(ReservationCommission, ReservationCommission.reservation_id == Reservation.id)
        .filter(Reservation.check_in == report_date)
        .filter(Reservation.status != ReservationStatus.CANCELLED)
        .group_by(Hotel.id, Hotel.name)
        .order_by(Hotel.name)
        .all()
    )
    items = [{"hotel_id": r.hotel_id, "hotel_name": r.hotel_name, "reservations": int(r.reservations), "revenue": float(r.revenue or 0), "commission": float(r.commission or 0)} for r in rows]
    return {
        "date": report_date,
        "total_reservations": sum(x["reservations"] for x in items),
        "total_revenue": sum(x["revenue"] for x in items),
        "total_commission": sum(x["commission"] for x in items),
        "hotels": items,
    }