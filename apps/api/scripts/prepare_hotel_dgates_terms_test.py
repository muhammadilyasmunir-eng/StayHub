"""Prepare HOTEL dGATES for the three-document approval test."""
from app.db.session import SessionLocal
from app.models.hotel import Hotel, HotelStatus
from app.models.terms_acceptance import HotelTermsAcceptance
from app.models.notification import Notification


def main():
    db = SessionLocal()
    try:
        hotel = db.query(Hotel).filter(Hotel.name.ilike("HOTEL dGATES")).order_by(Hotel.id.desc()).first()
        if not hotel:
            raise SystemExit("HOTEL dGATES was not found")
        db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id == hotel.id).delete(synchronize_session=False)
        db.query(Notification).filter(Notification.hotel_id == hotel.id, Notification.type.in_(["terms_required", "admin_review_required"])).delete(synchronize_session=False)
        hotel.status = HotelStatus.PENDING
        hotel.rejection_reason = None
        hotel.approved_at = None
        hotel.approved_by = None
        hotel.owner_documents_submitted = False
        db.commit()
        print(f"HOTEL dGATES is now PENDING. id={hotel.id}, owner_id={hotel.owner_id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
