from sqlalchemy.orm import Session

from app.models.hotel import Hotel
from app.models.user import User, UserRole
from app.schemas.hotel import HotelCreate, HotelUpdate


def get_hotel_by_id(db: Session, hotel_id: int):
    return (
        db.query(Hotel)
        .filter(Hotel.id == hotel_id)
        .first()
    )


def get_hotel_by_slug(db: Session, slug: str):
    return (
        db.query(Hotel)
        .filter(Hotel.slug == slug)
        .first()
    )


def get_hotel_by_email(db: Session, email: str):
    return (
        db.query(Hotel)
        .filter(Hotel.email == email)
        .first()
    )


def get_hotels(
    db: Session,
    owner_id: int,
):
    return (
        db.query(Hotel)
        .filter(Hotel.owner_id == owner_id)
        .all()
    )


def get_hotels_for_user(db: Session, user: User):
    """Return all properties for platform admins, owner-scoped properties otherwise."""
    if user.role == UserRole.ADMIN:
        return db.query(Hotel).all()
    return get_hotels(db=db, owner_id=user.id)


def create_hotel(
    db: Session,
    hotel: HotelCreate,
    owner_id: int,
):
    db_hotel = Hotel(
        owner_id=owner_id,
        **hotel.model_dump(),
    )

    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)

    return db_hotel


def update_hotel(
    db: Session,
    db_hotel: Hotel,
    hotel: HotelUpdate,
):
    data = hotel.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(db_hotel, key, value)

    db.commit()
    db.refresh(db_hotel)

    return db_hotel


def delete_hotel(
    db: Session,
    db_hotel: Hotel,
):
    db.delete(db_hotel)
    db.commit()
