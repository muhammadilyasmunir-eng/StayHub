from sqlalchemy.orm import Session

from app.models.room import Room
from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
)


def get_room_by_id(
    db: Session,
    room_id: int,
):
    return (
        db.query(Room)
        .filter(Room.id == room_id)
        .first()
    )


def get_room_by_number(
    db: Session,
    room_type_id: int,
    room_number: str,
):
    return (
        db.query(Room)
        .filter(
            Room.room_type_id == room_type_id,
            Room.room_number == room_number,
        )
        .first()
    )


def get_rooms(
    db: Session,
    room_type_id: int,
):
    return (
        db.query(Room)
        .filter(Room.room_type_id == room_type_id)
        .all()
    )


def create_room(
    db: Session,
    room: RoomCreate,
    room_type_id: int,
):
    db_room = Room(
        room_type_id=room_type_id,
        room_number=room.room_number,
        floor=room.floor,
        smoking=room.smoking,
        active=room.active,
        status=room.status,
    )

    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    return db_room


def update_room(
    db: Session,
    db_room: Room,
    room: RoomUpdate,
):
    update_data = room.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_room, key, value)

    db.commit()
    db.refresh(db_room)

    return db_room


def delete_room(
    db: Session,
    db_room: Room,
):
    db.delete(db_room)
    db.commit()

    return True