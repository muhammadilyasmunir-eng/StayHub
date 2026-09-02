from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.models.hotel import Hotel
from app.models.user import User
from app.schemas.guest import GuestCreate, GuestUpdate


class GuestService:

    def __init__(self, db: Session):
        self.db = db

    def _get_hotel(self, hotel_id: int, current_user: User) -> Hotel:
        hotel = (
            self.db.query(Hotel)
            .filter(
                Hotel.id == hotel_id,
                Hotel.owner_id == current_user.id,
            )
            .first()
        )

        if hotel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel not found",
            )

        return hotel

    def _get_guest(self, guest_id: int) -> Guest:
        guest = (
            self.db.query(Guest)
            .filter(Guest.id == guest_id)
            .first()
        )

        if guest is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Guest not found",
            )

        return guest

    def create_guest(
        self,
        hotel_id: int,
        payload: GuestCreate,
        current_user: User,
    ):
        self._get_hotel(hotel_id, current_user)

        guest = Guest(
            hotel_id=hotel_id,
            **payload.model_dump(),
        )

        self.db.add(guest)
        self.db.commit()
        self.db.refresh(guest)

        return guest

    def list_guests(
        self,
        hotel_id: int,
        current_user: User,
    ):
        self._get_hotel(hotel_id, current_user)

        return (
            self.db.query(Guest)
            .filter(Guest.hotel_id == hotel_id)
            .all()
        )

    def get_guest(
        self,
        guest_id: int,
        current_user: User,
    ):
        guest = self._get_guest(guest_id)

        self._get_hotel(
            guest.hotel_id,
            current_user,
        )

        return guest

    def update_guest(
        self,
        guest_id: int,
        payload: GuestUpdate,
        current_user: User,
    ):
        guest = self._get_guest(guest_id)

        self._get_hotel(
            guest.hotel_id,
            current_user,
        )

        data = payload.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(guest, key, value)

        self.db.commit()
        self.db.refresh(guest)

        return guest

    def delete_guest(
        self,
        guest_id: int,
        current_user: User,
    ):
        guest = self._get_guest(guest_id)

        self._get_hotel(
            guest.hotel_id,
            current_user,
        )

        self.db.delete(guest)
        self.db.commit()