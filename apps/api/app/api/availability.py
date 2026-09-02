from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.hotel import Hotel
from app.models.reservation import Reservation, ReservationStatus
from app.models.room_type import RoomType
from app.models.room_availability import RoomAvailability
from app.models.user import User

router = APIRouter(prefix="/availability", tags=["Availability"])


def owner_room_types(db: Session, hotel_id: int, user: User):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == user.id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return db.query(RoomType).filter(RoomType.hotel_id == hotel_id).order_by(RoomType.id).all()


def booked_by_day(db: Session, room_type_id: int, start: date, end: date):
    rows = db.query(Reservation).join(Reservation.room).filter(
        Reservation.check_in < end,
        Reservation.check_out > start,
        Reservation.status.notin_([ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]),
        Reservation.room.has(room_type_id=room_type_id),
    ).all()
    booked = {}
    for r in rows:
        d = max(start, r.check_in)
        last = min(end, r.check_out)
        while d < last:
            booked[d] = booked.get(d, 0) + 1
            d += timedelta(days=1)
    return booked


@router.get("/hotel/{hotel_id}")
def get_calendar(
    hotel_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    room_type_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if end_date <= start_date or (end_date - start_date).days > 62:
        raise HTTPException(status_code=400, detail="Select a valid date range up to 62 days")
    types = owner_room_types(db, hotel_id, current_user)
    if room_type_id:
        types = [t for t in types if t.id == room_type_id]
    days = []
    d = start_date
    while d < end_date:
        days.append(d)
        d += timedelta(days=1)
    output = []
    for rt in types:
        rows = {x.date: x for x in db.query(RoomAvailability).filter(RoomAvailability.room_type_id == rt.id, RoomAvailability.date >= start_date, RoomAvailability.date < end_date).all()}
        booked = booked_by_day(db, rt.id, start_date, end_date)
        cells = []
        for day in days:
            row = rows.get(day)
            rooms_to_sell = min(int(row.rooms_to_sell if row else rt.number_of_rooms), int(rt.number_of_rooms))
            rate = float(row.rate if row else rt.base_price)
            bookable = row.bookable if row else bool(rt.status)
            cells.append({"date": day.isoformat(), "rooms_to_sell": rooms_to_sell, "net_booked": booked.get(day, 0), "available": max(0, rooms_to_sell - booked.get(day, 0)), "rate": rate, "bookable": bookable})
        output.append({"room_type_id": rt.id, "name": rt.name, "inventory": rt.number_of_rooms, "base_rate": float(rt.base_price), "cells": cells})
    return {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "days": [d.isoformat() for d in days], "room_types": output}


@router.put("/hotel/{hotel_id}")
def update_calendar(
    hotel_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    types = {t.id: t for t in owner_room_types(db, hotel_id, current_user)}
    items = payload.get("items") or []
    if not items or len(items) > 500:
        raise HTTPException(status_code=400, detail="Provide 1 to 500 calendar updates")
    for item in items:
        rt_id = int(item["room_type_id"]); day = date.fromisoformat(item["date"])
        rt = types.get(rt_id)
        if not rt:
            raise HTTPException(status_code=404, detail="Room type not found")
        rooms = max(0, int(item.get("rooms_to_sell", rt.number_of_rooms)))
        if rooms > int(rt.number_of_rooms):
            raise HTTPException(status_code=400, detail=f"Rooms to sell cannot exceed inventory ({rt.number_of_rooms}) for {rt.name} on {day}")
        rate = float(item.get("rate", rt.base_price))
        if rate < 0:
            raise HTTPException(status_code=400, detail="Rate cannot be negative")
        bookable = bool(item.get("bookable", True))
        booked = booked_by_day(db, rt.id, day, day + timedelta(days=1)).get(day, 0)
        if rooms < booked:
            raise HTTPException(status_code=400, detail=f"Rooms to sell cannot be below net booked ({booked}) for {rt.name} on {day}")
        row = db.query(RoomAvailability).filter(RoomAvailability.room_type_id == rt.id, RoomAvailability.date == day).first()
        if not row:
            row = RoomAvailability(room_type_id=rt.id, date=day)
            db.add(row)
        row.rooms_to_sell = rooms; row.rate = rate; row.bookable = bookable
    db.commit()
    return {"message": "Calendar updated", "updated": len(items)}
