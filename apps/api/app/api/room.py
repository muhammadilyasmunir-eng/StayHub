from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user

from app.models.user import User
from app.models.hotel import Hotel
from app.models.room_type import RoomType

from app.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
)

from app.services.room_service import (
    create_room,
    delete_room,
    get_room_by_id,
    get_room_by_number,
    get_rooms,
    update_room,
)

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


@router.post(
    "/room-type/{room_type_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    room_type_id: int,
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if room_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    hotel = db.query(Hotel).filter(
        Hotel.id == room_type.hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    if get_room_by_number(db, room_type_id, room.room_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room number already exists")

    return create_room(db=db, room=room, room_type_id=room_type_id)


@router.get(
    "/hotel/{hotel_id}",
    response_model=list[RoomResponse],
)
def list_hotel_rooms(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all rooms belonging to an owner-controlled hotel."""
    hotel = db.query(Hotel).filter(
        Hotel.id == hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")

    room_type_ids = [row[0] for row in db.query(RoomType.id).filter(RoomType.hotel_id == hotel_id).all()]
    if not room_type_ids:
        return []

    rooms = []
    for room_type_id in room_type_ids:
        rooms.extend(get_rooms(db=db, room_type_id=room_type_id))
    return rooms


@router.get(
    "/room-type/{room_type_id}",
    response_model=list[RoomResponse],
)
def list_rooms(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if room_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    hotel = db.query(Hotel).filter(
        Hotel.id == room_type.hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    return get_rooms(db=db, room_type_id=room_type_id)


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
def get(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    room_type = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
    hotel = db.query(Hotel).filter(
        Hotel.id == room_type.hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    return room


@router.put(
    "/{room_id}",
    response_model=RoomResponse,
)
def update(
    room_id: int,
    room: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_room = get_room_by_id(db, room_id)
    if db_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    room_type = db.query(RoomType).filter(RoomType.id == db_room.room_type_id).first()
    hotel = db.query(Hotel).filter(
        Hotel.id == room_type.hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if room.room_number and room.room_number != db_room.room_number:
        if get_room_by_number(db, db_room.room_type_id, room.room_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room number already exists")

    return update_room(db=db, db_room=db_room, room=room)


@router.delete(
    "/{room_id}",
)
def delete(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_room = get_room_by_id(db, room_id)
    if db_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    room_type = db.query(RoomType).filter(RoomType.id == db_room.room_type_id).first()
    hotel = db.query(Hotel).filter(
        Hotel.id == room_type.hotel_id,
        Hotel.owner_id == current_user.id,
    ).first()
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    delete_room(db=db, db_room=db_room)
    return {"message": "Room deleted successfully"}
