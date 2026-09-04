from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.hotel import Hotel
from app.models.room_type import RoomType
from app.models.room_type_facility import RoomTypeFacility
from app.models.user import User

router = APIRouter(prefix="/room-amenities", tags=["Room Amenities"])


@router.get("/hotel/{hotel_id}")
def get_room_amenities(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == current_user.id).first()
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room_types = (
        db.query(RoomType)
        .filter(RoomType.hotel_id == hotel.id, RoomType.status.is_(True))
        .order_by(RoomType.id)
        .all()
    )
    facilities = db.query(RoomTypeFacility).join(RoomType).filter(RoomType.hotel_id == hotel.id).all()

    by_name: dict[str, set[int]] = {}
    for facility in facilities:
        if facility.available:
            by_name.setdefault(facility.name, set()).add(facility.room_type_id)

    return {
        "hotel_id": hotel.id,
        "unit": "sqm",
        "room_types": [
            {"id": room.id, "name": room.name, "room_size": room.room_size}
            for room in room_types
        ],
        "amenities": {
            name: sorted(room_ids)
            for name, room_ids in by_name.items()
        },
    }


@router.put("/hotel/{hotel_id}")
def save_room_amenities(
    hotel_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == current_user.id).first()
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room_types = (
        db.query(RoomType)
        .filter(RoomType.hotel_id == hotel.id, RoomType.status.is_(True))
        .order_by(RoomType.id)
        .all()
    )
    room_ids = {room.id for room in room_types}
    room_sizes = payload.get("room_sizes") or {}
    amenities = payload.get("amenities") or {}

    for room in room_types:
        if str(room.id) in room_sizes:
            value = room_sizes[str(room.id)]
            if value is None or not str(value).strip():
                room.room_size = None
            else:
                room.room_size = str(value).strip()[:100]

    for name, config in amenities.items():
        if not isinstance(name, str) or not name.strip():
            continue
        config = config if isinstance(config, dict) else {}
        state = config.get("state", "none")
        selected = config.get("room_type_ids") or []
        if state == "all":
            selected_ids = room_ids
        elif state == "some":
            selected_ids = {int(value) for value in selected if str(value).isdigit() and int(value) in room_ids}
        else:
            selected_ids = set()

        existing = db.query(RoomTypeFacility).join(RoomType).filter(
            RoomType.hotel_id == hotel.id,
            RoomTypeFacility.name == name.strip(),
        ).all()
        for facility in existing:
            db.delete(facility)
        for room_id in selected_ids:
            db.add(RoomTypeFacility(room_type_id=room_id, name=name.strip()[:150], available=True))

    db.commit()
    return {"message": "Room amenities saved successfully"}
