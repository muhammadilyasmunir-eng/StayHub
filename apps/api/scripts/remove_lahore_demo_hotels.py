"""Remove the five Lahore demo properties previously seeded by StayHub.

Run from apps/api:
    python scripts/remove_lahore_demo_hotels.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.hotel import Hotel

PROPERTY_IDS = {
    "SH-LHR-DGATES",
    "SH-LHR-BWPREMIER",
    "SH-LHR-AVARI",
    "SH-LHR-PC",
    "SH-LHR-INDIGO",
}

DEMO_EMAILS = {
    "muhammadilyasmunir@gmail.com",
    "muhammadilyasmunir01@gmail.com",
    "muhammadilyasmunir02@gmail.com",
    "muhammadilyasmunir03@gmail.com",
    "muhammadilyasmunir04@gmail.com",
}


def remove_demo_hotels() -> None:
    db = SessionLocal()
    try:
        rows = db.query(Hotel).filter(
            (Hotel.property_id.in_(PROPERTY_IDS)) | (Hotel.email.in_(DEMO_EMAILS))
        ).all()
        for hotel in rows:
            print(f"Removing demo property: {hotel.property_id} | {hotel.name}")
            db.delete(hotel)
        db.commit()
        print(f"Removed {len(rows)} Lahore demo property record(s).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    remove_demo_hotels()
