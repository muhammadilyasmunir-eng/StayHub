from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.dependencies import get_current_user

from app.models.user import User

from app.schemas.guest import (
    GuestCreate,
    GuestUpdate,
    GuestResponse,
)

from app.services.guest_service import GuestService


router = APIRouter(
    prefix="/guests",
    tags=["Guests"],
)


@router.post(
    "/hotel/{hotel_id}",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guest(
    hotel_id: int,
    payload: GuestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = GuestService(db)

    return service.create_guest(
        hotel_id=hotel_id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/hotel/{hotel_id}",
    response_model=List[GuestResponse],
)
def list_guests(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = GuestService(db)

    return service.list_guests(
        hotel_id=hotel_id,
        current_user=current_user,
    )


@router.get(
    "/{guest_id}",
    response_model=GuestResponse,
)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = GuestService(db)

    return service.get_guest(
        guest_id=guest_id,
        current_user=current_user,
    )


@router.put(
    "/{guest_id}",
    response_model=GuestResponse,
)
def update_guest(
    guest_id: int,
    payload: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = GuestService(db)

    return service.update_guest(
        guest_id=guest_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{guest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = GuestService(db)

    service.delete_guest(
        guest_id=guest_id,
        current_user=current_user,
    )