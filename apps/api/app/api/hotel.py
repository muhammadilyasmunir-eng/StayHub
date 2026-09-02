from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.hotel import Hotel, HotelStatus
from app.schemas.hotel import (
    HotelCreate,
    HotelUpdate,
    HotelResponse,
)
from app.services.hotel_service import (
    create_hotel,
    get_hotels_for_user,
    get_hotel_by_id,
    get_hotel_by_slug,
    get_hotel_by_email,
    update_hotel,
    delete_hotel,
)

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"],
)


@router.post(
    "/",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    hotel: HotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if get_hotel_by_email(db, hotel.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel email already exists")
    if get_hotel_by_slug(db, hotel.slug):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel slug already exists")
    if db.query(Hotel).filter(Hotel.property_id == hotel.property_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel licence number / Property ID already exists")
    return create_hotel(db=db, hotel=hotel, owner_id=current_user.id)


@router.get("/", response_model=list[HotelResponse])
def list_hotels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_hotels_for_user(db=db, user=current_user)


@router.get("/{slug}", response_model=HotelResponse)
def get_hotel(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = get_hotel_by_slug(db, slug)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return hotel


@router.put("/{hotel_id}", response_model=HotelResponse)
def update(hotel_id: int, hotel: HotelUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_hotel = get_hotel_by_id(db, hotel_id)
    if db_hotel is None or db_hotel.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    return update_hotel(db=db, db_hotel=db_hotel, hotel=hotel)


@router.post("/{hotel_id}/resubmit", response_model=HotelResponse)
def resubmit_rejected_hotel(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Owner acknowledges the rejection, after editing the property, and sends it back to admin review."""
    hotel = get_hotel_by_id(db, hotel_id)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    if hotel.status != HotelStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only rejected properties can be resubmitted")

    hotel.status = HotelStatus.PENDING
    # Keep the rejection reason as audit/history; the owner UI displays it as the review notification.
    hotel.approved_at = None
    hotel.approved_by = None
    db.commit()
    db.refresh(hotel)
    return hotel


@router.delete("/{hotel_id}")
def delete(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_hotel = get_hotel_by_id(db, hotel_id)
    if db_hotel is None or db_hotel.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
    delete_hotel(db=db, db_hotel=db_hotel)
    return {"message": "Hotel deleted successfully"}
