from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import require_hotel_owner
from app.models.hotel import Hotel
from app.models.user import User
from app.api.reservation import serialize
from app.services.commission_service import sync_commission_status
from app.services.reservation_service import get_reservations

router = APIRouter(prefix="/reservations", tags=["Owner Reservation Compatibility"])

@router.get("/hotel")
def get_owner_reservations_without_hotel(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hotel_owner),
):
    """Backward-compatible owner endpoint used when the portal has not stored hotel_id yet."""
    hotels = db.query(Hotel).filter(Hotel.owner_id == current_user.id).order_by(Hotel.id.asc()).all()
    if not hotels:
        return []
    result = []
    for hotel in hotels:
        for reservation in get_reservations(db=db, hotel_id=hotel.id):
            commission = sync_commission_status(db, reservation)
            result.append(serialize(reservation, commission_override=commission, db=db))
    db.commit()
    return result
