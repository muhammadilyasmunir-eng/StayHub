from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.hotel import Hotel
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
)
from app.services.hotel_service import get_hotel_by_id
from app.services.reservation_service import (
    create_reservation,
    get_reservations,
    get_reservation_by_id,
    update_reservation,
    delete_reservation,
    room_is_available,
)

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)


@router.post(
    "/hotel/{hotel_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    hotel_id: int,
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    hotel = get_hotel_by_id(db, hotel_id)

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    if hotel.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    if not room_is_available(
        db,
        reservation.room_id,
        reservation.check_in,
        reservation.check_out,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for selected dates",
        )

    return create_reservation(
        db=db,
        hotel_id=hotel_id,
        reservation=reservation,
    )


@router.get(
    "/hotel/{hotel_id}",
    response_model=list[ReservationResponse],
)
def list_reservations(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    hotel = get_hotel_by_id(db, hotel_id)

    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Hotel not found",
        )

    return get_reservations(
        db=db,
        hotel_id=hotel_id,
    )


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
)
def get(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    reservation = get_reservation_by_id(
        db,
        reservation_id,
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    hotel = get_hotel_by_id(
        db,
        reservation.hotel_id,
    )

    if hotel.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    return reservation


@router.put(
    "/{reservation_id}",
    response_model=ReservationResponse,
)
def update(
    reservation_id: int,
    reservation: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    db_reservation = get_reservation_by_id(
        db,
        reservation_id,
    )

    if db_reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    hotel = get_hotel_by_id(
        db,
        db_reservation.hotel_id,
    )

    if hotel.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    return update_reservation(
        db=db,
        db_reservation=db_reservation,
        reservation=reservation,
    )


@router.delete(
    "/{reservation_id}",
)
def delete(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    reservation = get_reservation_by_id(
        db,
        reservation_id,
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    hotel = get_hotel_by_id(
        db,
        reservation.hotel_id,
    )

    if hotel.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    delete_reservation(
        db=db,
        db_reservation=reservation,
    )

    return {
        "message": "Reservation deleted successfully"
    }