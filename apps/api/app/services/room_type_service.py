from sqlalchemy.orm import Session

from app.models.room_type import RoomType
from app.models.room_availability import RoomAvailability
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate


def get_room_type_by_id(db: Session, room_type_id: int):
    return db.query(RoomType).filter(RoomType.id == room_type_id).first()


def get_room_types(db: Session, hotel_id: int):
    return db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()


def create_room_type(db: Session, room_type: RoomTypeCreate, hotel_id: int):
    db_room_type = RoomType(
        hotel_id=hotel_id,
        name=room_type.name,
        description=room_type.description,
        number_of_rooms=room_type.number_of_rooms,
        max_adults=room_type.max_adults,
        max_children=room_type.max_children,
        base_price=room_type.base_price,
        discount_percent=room_type.discount_percent,
        status=room_type.status,
    )
    db.add(db_room_type)
    db.flush()
    db.commit()
    db.refresh(db_room_type)
    return db_room_type


def update_room_type(db: Session, db_room_type: RoomType, room_type: RoomTypeUpdate):
    update_data = room_type.model_dump(exclude_unset=True)
    new_inventory = update_data.get("number_of_rooms")
    if new_inventory is not None:
        new_inventory = int(new_inventory)
        if new_inventory < 1:
            raise ValueError("number_of_rooms must be at least 1")
        # Rooms to Sell is the master inventory quantity. When the owner
        # changes it in Room Types, every existing calendar Sell value for
        # this room type must follow the new quantity.
        rows = db.query(RoomAvailability).filter(RoomAvailability.room_type_id == db_room_type.id).all()
        for row in rows:
            row.rooms_to_sell = new_inventory
    for key, value in update_data.items():
        setattr(db_room_type, key, value)
    db.commit()
    db.refresh(db_room_type)
    return db_room_type


def delete_room_type(db: Session, db_room_type: RoomType):
    db.delete(db_room_type)
    db.commit()
    return True
