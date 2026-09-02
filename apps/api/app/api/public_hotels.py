from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hotel import Hotel, HotelStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import Room, RoomStatus
from app.models.room_availability import RoomAvailability
from app.services.pricing import calculate_room_price

router = APIRouter(prefix="/public/hotels", tags=["Public Hotels"])


def serialize_public_hotel(hotel: Hotel):
    primary = next((photo for photo in hotel.photos if photo.is_primary), None)
    billing_ready = hotel.tax_percent is not None and hotel.commission_percent is not None
    return {
        "id": hotel.id, "property_id": hotel.property_id, "name": hotel.name, "slug": hotel.slug,
        "property_type": hotel.property_type, "description": hotel.description, "star_rating": hotel.star_rating,
        "country": hotel.country, "city": hotel.city, "address": hotel.address, "postal_code": hotel.postal_code,
        "total_rooms": hotel.total_rooms, "check_in_time": hotel.check_in_time, "check_out_time": hotel.check_out_time,
        "currency": hotel.currency, "tax_percent": float(hotel.tax_percent or 0), "booking_enabled": billing_ready,
        "booking_disabled_reason": None if billing_ready else "Reservations are temporarily unavailable until StayHub admin configures property tax and commission.",
        "primary_photo": primary.photo_url if primary else None,
        "facilities": [item.name for item in hotel.facilities if item.available],
    }


def _calendar_rows(db: Session, room_type_id: int, check_in: date | None, check_out: date | None):
    if check_in is None or check_out is None:
        return {}
    try:
        rows = db.query(RoomAvailability).filter(
            RoomAvailability.room_type_id == room_type_id,
            RoomAvailability.date >= check_in,
            RoomAvailability.date < check_out,
        ).all()
    except SQLAlchemyError:
        db.rollback()
        return {}
    return {row.date: row for row in rows}


def _booked_by_day(db: Session, room_type_id: int, check_in: date, check_out: date):
    try:
        rows = db.query(Reservation).join(Room, Reservation.room_id == Room.id).filter(
            Room.room_type_id == room_type_id,
            Reservation.check_in < check_out,
            Reservation.check_out > check_in,
            Reservation.status.notin_([ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]),
        ).all()
    except SQLAlchemyError:
        db.rollback()
        return {}
    booked = {}
    for reservation in rows:
        d = max(check_in, reservation.check_in)
        last = min(check_out, reservation.check_out)
        while d < last:
            booked[d] = booked.get(d, 0) + 1
            d += timedelta(days=1)
    return booked


def _room_is_available_for_dates(room: Room, check_in: date | None, check_out: date | None) -> bool:
    if not room.active:
        return False
    if room.status in (RoomStatus.MAINTENANCE, RoomStatus.OUT_OF_ORDER):
        return False
    if check_in is None or check_out is None:
        return room.status == RoomStatus.AVAILABLE
    if check_out <= check_in:
        return False
    for reservation in room.reservations:
        if reservation.status in (ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW):
            continue
        if reservation.check_in < check_out and reservation.check_out > check_in:
            return False
    return True


def _price_value(price, field):
    if isinstance(price, dict):
        return price.get(field, 0)
    return getattr(price, field, 0)


def serialize_room(db: Session, room_type, hotel_tax, check_in: date | None = None, check_out: date | None = None):
    rows = _calendar_rows(db, room_type.id, check_in, check_out)
    booked = _booked_by_day(db, room_type.id, check_in, check_out) if check_in and check_out else {}
    daily = []
    if check_in and check_out:
        d = check_in
        while d < check_out:
            row = rows.get(d)
            rooms_to_sell = int(row.rooms_to_sell) if row else int(room_type.number_of_rooms or 0)
            rate_base = Decimal(str(row.rate if row else room_type.base_price or 0))
            net_booked = booked.get(d, 0)
            available = max(0, rooms_to_sell - net_booked)
            bookable = bool(row.bookable) if row else bool(room_type.status)
            price = calculate_room_price(rate_base, Decimal(str(room_type.discount_percent or 0)), Decimal(str(hotel_tax or 0)))
            daily.append({"date": d, "rate": float(_price_value(price, "base_price")), "base_price": float(_price_value(price, "base_price")), "selling_price": float(_price_value(price, "selling_price")), "total_price": float(_price_value(price, "total_price")), "discount_percent": float(_price_value(price, "discount_percent")), "discount_amount": float(_price_value(price, "discount_amount")), "tax_amount": float(_price_value(price, "tax_amount")), "rooms_to_sell": rooms_to_sell, "net_booked": net_booked, "available": available, "bookable": bookable})
            d += timedelta(days=1)
        if not daily or any(not x["bookable"] or x["available"] <= 0 for x in daily):
            return None
        price = daily[0]
    else:
        price = calculate_room_price(Decimal(str(room_type.base_price or 0)), Decimal(str(room_type.discount_percent or 0)), Decimal(str(hotel_tax or 0)))

    return {
        "id": room_type.id, "room_type_id": room_type.id, "name": room_type.name, "description": room_type.description,
        "number_of_rooms": room_type.number_of_rooms, "max_adults": room_type.max_adults, "max_children": room_type.max_children,
        "bed_type": room_type.bed_type, "room_size": room_type.room_size, "base_price": float(_price_value(price, "base_price")),
        "discount_percent": float(_price_value(price, "discount_percent")), "discount_amount": float(_price_value(price, "discount_amount")),
        "selling_price": float(_price_value(price, "selling_price")), "tax_percent": float(_price_value(price, "tax_percent")),
        "tax_amount": float(_price_value(price, "tax_amount")), "total_price": float(_price_value(price, "total_price")), "calendar": daily,
        "facilities": [facility.name for facility in room_type.facilities if facility.available],
        "photos": [{"url": photo.photo_url, "caption": photo.caption, "is_primary": photo.is_primary, "sort_order": photo.sort_order} for photo in sorted(room_type.photos, key=lambda photo: photo.sort_order)],
    }


def _lowest_available_rate(db: Session, hotel: Hotel, check_in: date | None, check_out: date | None):
    candidates = []
    for room_type in hotel.room_types:
        if not room_type.status:
            continue
        data = serialize_room(db, room_type, hotel.tax_percent, check_in, check_out)
        if data is None:
            continue
        candidates.append({"room_type_id": room_type.id, "selling_price": data["selling_price"], "total_price": data["total_price"], "currency": hotel.currency})
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item["total_price"], item["selling_price"]))


@router.get("/")
def list_public_hotels(city: str | None = None, country: str | None = None, property_type: str | None = None,
                      check_in: date | None = None, check_out: date | None = None, db: Session = Depends(get_db)):
    if (check_in is None) != (check_out is None):
        raise HTTPException(status_code=400, detail="check_in and check_out must be provided together")
    if check_in is not None and check_out <= check_in:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")
    query = db.query(Hotel).filter(Hotel.status == HotelStatus.APPROVED)
    if city: query = query.filter(Hotel.city.ilike(f"%{city.strip()}%"))
    if country: query = query.filter(Hotel.country.ilike(f"%{country.strip()}%"))
    if property_type: query = query.filter(Hotel.property_type == property_type.strip())
    results = []
    for hotel in query.all():
        lowest = _lowest_available_rate(db, hotel, check_in, check_out)
        if lowest is None: continue
        data = serialize_public_hotel(hotel)
        data.update({"rating": hotel.star_rating, "rating_type": "star_rating", "review_count": None, "lowest_available_rate": lowest["selling_price"], "lowest_available_total": lowest["total_price"], "lowest_available_currency": lowest["currency"], "lowest_available_room_type_id": lowest["room_type_id"], "availability_check_in": check_in, "availability_check_out": check_out})
        results.append(data)
    results.sort(key=lambda item: (-(float(item["star_rating"]) if item["star_rating"] is not None else -1), float(item["lowest_available_total"]), item["name"].lower()))
    return results


@router.get("/{slug}")
def get_public_hotel(slug: str, check_in: date | None = None, check_out: date | None = None, db: Session = Depends(get_db)):
    if (check_in is None) != (check_out is None): raise HTTPException(status_code=400, detail="check_in and check_out must be provided together")
    if check_in is not None and check_out <= check_in: raise HTTPException(status_code=400, detail="check_out must be after check_in")
    hotel = db.query(Hotel).filter(Hotel.slug == slug, Hotel.status == HotelStatus.APPROVED).first()
    if hotel is None: raise HTTPException(status_code=404, detail="Property not found")
    data = serialize_public_hotel(hotel)
    rooms = [serialize_room(db, room_type, hotel.tax_percent, check_in, check_out) for room_type in hotel.room_types if room_type.status]
    rooms = [room for room in rooms if room is not None]
    data.update({"website": hotel.website, "phone": hotel.phone, "alternate_phone": hotel.alternate_phone, "latitude": hotel.latitude, "longitude": hotel.longitude,
                 "photos": [{"url": photo.photo_url, "caption": photo.caption, "category": photo.category, "is_primary": photo.is_primary, "sort_order": photo.sort_order} for photo in sorted(hotel.photos, key=lambda photo: photo.sort_order)],
                 "rooms": rooms, "availability_check_in": check_in, "availability_check_out": check_out})
    return data
