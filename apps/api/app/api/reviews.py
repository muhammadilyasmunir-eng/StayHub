from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import require_admin, require_customer, require_hotel_owner
from app.models.guest import Guest
from app.models.hotel import Hotel, HotelStatus
from app.models.notification import Notification
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User, UserRole
from app.models.guest_review import GuestReview

router = APIRouter(tags=["Reviews"])

class ReviewPayload(BaseModel):
    overall_score: float = Field(ge=1, le=10)
    staff_score: float = Field(ge=1, le=10)
    facilities_score: float = Field(ge=1, le=10)
    cleanliness_score: float = Field(ge=1, le=10)
    comfort_score: float = Field(ge=1, le=10)
    value_score: float = Field(ge=1, le=10)
    location_score: float = Field(ge=1, le=10)
    wifi_score: float = Field(ge=1, le=10)
    title: str | None = Field(default=None, max_length=200)
    comment: str = Field(min_length=3, max_length=5000)

class OwnerReplyPayload(BaseModel):
    reply: str = Field(min_length=2, max_length=5000)

class AdminReviewPayload(ReviewPayload):
    admin_note: str | None = Field(default=None, max_length=2000)


def _now(): return datetime.now(timezone.utc)

def _customer_reservation(db: Session, reservation_id: int, user: User):
    guest_ids = [g.id for g in db.query(Guest).filter(Guest.email.ilike(user.email)).all()]
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.guest_id.in_(guest_ids)).first()
    if not reservation: raise HTTPException(404, "Reservation not found")
    return reservation

def _payload(review: GuestReview, include_private=True):
    r, g, h = review.reservation, review.guest, review.hotel
    deadline = review.created_at + timedelta(days=7) if review.created_at else None
    return {"id": review.id, "reservation_id": review.reservation_id, "confirmation_no": r.confirmation_no if r else None, "hotel_id": review.hotel_id, "hotel_name": h.name if h else None, "guest_id": review.guest_id, "guest_name": f"{g.first_name} {g.last_name}".strip() if g else "Guest", "guest_country": g.country if g else None, "room_type": r.room.room_type.name if r and r.room and r.room.room_type else None, "check_out": r.check_out if r else None, "created_at": review.created_at, "updated_at": review.updated_at, "edit_deadline": deadline, "edit_expired": bool(deadline and _now() > deadline), "deleted": bool(review.deleted_at), "overall_score": review.overall_score, "staff_score": review.staff_score, "facilities_score": review.facilities_score, "cleanliness_score": review.cleanliness_score, "comfort_score": review.comfort_score, "value_score": review.value_score, "location_score": review.location_score, "wifi_score": review.wifi_score, "title": review.title, "comment": review.comment, "owner_reply": review.owner_reply, "owner_reply_at": review.owner_reply_at, "categories": {"Staff": review.staff_score, "Facilities": review.facilities_score, "Cleanliness": review.cleanliness_score, "Comfort": review.comfort_score, "Value for money": review.value_score, "Location": review.location_score, "Free Wifi": review.wifi_score}, **({"admin_note": review.admin_note} if include_private else {})}

def _eligible(reservation):
    return reservation.status in (ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT) and bool(reservation.check_out) and date.today() >= reservation.check_out

def _ensure_after_checkout(reservation):
    if not _eligible(reservation): raise HTTPException(400, "The Review option becomes available after check-out")

@router.get("/customer/reservations/{reservation_id}/review")
def customer_review(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _customer_reservation(db, reservation_id, current_user); review = db.query(GuestReview).filter(GuestReview.reservation_id == reservation.id).first()
    return {"eligible": _eligible(reservation), "review": _payload(review) if review else None}

@router.post("/customer/reservations/{reservation_id}/review")
def create_review(reservation_id: int, payload: ReviewPayload, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _customer_reservation(db, reservation_id, current_user); _ensure_after_checkout(reservation)
    if db.query(GuestReview).filter(GuestReview.reservation_id == reservation.id).first(): raise HTTPException(409, "A review has already been submitted for this reservation and cannot be submitted again.")
    review = GuestReview(reservation_id=reservation.id, hotel_id=reservation.hotel_id, guest_id=reservation.guest_id, customer_user_id=current_user.id, **payload.model_dump()); db.add(review); db.flush()
    owner_id = reservation.hotel.owner_id if reservation.hotel else None
    guest_name = f"{reservation.guest.first_name} {reservation.guest.last_name}".strip() if reservation.guest else "Guest"
    message = f"Reservation #{reservation.confirmation_no} • {guest_name} • {review.overall_score:.1f}/10 • {reservation.hotel.name if reservation.hotel else 'Property'}"
    if owner_id:
        db.add(Notification(user_id=owner_id, hotel_id=reservation.hotel_id, title="New guest review", message=message, type="guest_review"))
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    for admin in admins:
        db.add(Notification(user_id=admin.id, hotel_id=reservation.hotel_id, title="New guest review", message=message, type="guest_review"))
    db.commit(); db.refresh(review)
    return _payload(review)

@router.put("/customer/reservations/{reservation_id}/review")
def update_review(reservation_id: int, payload: ReviewPayload, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _customer_reservation(db, reservation_id, current_user); review = db.query(GuestReview).filter(GuestReview.reservation_id == reservation.id, GuestReview.customer_user_id == current_user.id).first()
    if not review: raise HTTPException(404, "Review not found")
    if review.deleted_at: raise HTTPException(400, "This review has been deleted and cannot be submitted again")
    if review.created_at and _now() > review.created_at + timedelta(days=7): raise HTTPException(400, "The 7-day review editing period has expired. You can only delete the review now.")
    for key, value in payload.model_dump().items(): setattr(review, key, value)
    db.commit(); db.refresh(review); return _payload(review)

@router.delete("/customer/reservations/{reservation_id}/review")
def delete_review(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _customer_reservation(db, reservation_id, current_user); review = db.query(GuestReview).filter(GuestReview.reservation_id == reservation.id, GuestReview.customer_user_id == current_user.id).first()
    if not review: raise HTTPException(404, "Review not found")
    if review.deleted_at: raise HTTPException(400, "This review has already been deleted")
    review.deleted_at, review.deleted_by = _now(), "guest"; db.commit(); return {"message": "Review deleted. You cannot submit another review for this reservation."}

@router.get("/owner/reviews")
def owner_reviews(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_hotel_owner)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == current_user.id).first()
    if not hotel: raise HTTPException(404, "Property not found")
    return [_payload(x, include_private=False) for x in db.query(GuestReview).filter(GuestReview.hotel_id == hotel_id, GuestReview.deleted_at.is_(None)).order_by(GuestReview.created_at.desc()).all()]

@router.put("/owner/reviews/{review_id}/reply")
def owner_reply(review_id: int, payload: OwnerReplyPayload, db: Session = Depends(get_db), current_user: User = Depends(require_hotel_owner)):
    review = db.query(GuestReview).filter(GuestReview.id == review_id, GuestReview.deleted_at.is_(None)).first()
    if not review or not review.hotel or review.hotel.owner_id != current_user.id: raise HTTPException(404, "Review not found")
    review.owner_reply, review.owner_reply_at = payload.reply.strip(), _now(); db.commit(); db.refresh(review); return _payload(review, include_private=False)

@router.get("/admin/reviews")
def admin_reviews(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return [_payload(x) for x in db.query(GuestReview).order_by(GuestReview.created_at.desc()).all()]

@router.put("/admin/reviews/{review_id}")
def admin_update_review(review_id: int, payload: AdminReviewPayload, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    review = db.query(GuestReview).filter(GuestReview.id == review_id).first()
    if not review: raise HTTPException(404, "Review not found")
    for key, value in payload.model_dump().items(): setattr(review, key, value)
    db.commit(); db.refresh(review); return _payload(review)

@router.delete("/admin/reviews/{review_id}")
def admin_delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    review = db.query(GuestReview).filter(GuestReview.id == review_id).first()
    if not review: raise HTTPException(404, "Review not found")
    review.deleted_at, review.deleted_by = _now(), "admin"; db.commit(); return {"message": "Review removed from StayHub public listings."}

@router.get("/public/hotels/{slug}/reviews")
def public_hotel_reviews(slug: str, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.slug == slug, Hotel.status == HotelStatus.APPROVED).first()
    if not hotel: raise HTTPException(404, "Property not found")
    rows = db.query(GuestReview).filter(GuestReview.hotel_id == hotel.id, GuestReview.deleted_at.is_(None)).order_by(GuestReview.created_at.desc()).all()
    def avg(field): return round(float(db.query(func.avg(field)).filter(GuestReview.hotel_id == hotel.id, GuestReview.deleted_at.is_(None)).scalar() or 0), 1)
    return {"hotel_id": hotel.id, "hotel_name": hotel.name, "count": len(rows), "overall_score": avg(GuestReview.overall_score), "categories": {"Staff": avg(GuestReview.staff_score), "Facilities": avg(GuestReview.facilities_score), "Cleanliness": avg(GuestReview.cleanliness_score), "Comfort": avg(GuestReview.comfort_score), "Value for money": avg(GuestReview.value_score), "Location": avg(GuestReview.location_score), "Free Wifi": avg(GuestReview.wifi_score)}, "reviews": [_payload(x, include_private=False) for x in rows]}
