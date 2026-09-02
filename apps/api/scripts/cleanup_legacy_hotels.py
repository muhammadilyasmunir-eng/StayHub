"""Safely remove legacy demo hotels 600001/600002 and their dependent rows."""

from pathlib import Path
import sys

# Allow `python scripts/cleanup_legacy_hotels.py` from apps/api.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.hotel import Hotel

LEGACY_PROPERTY_IDS = {"600001", "600002"}
LEGACY_NAMES = {"Hotel dGATES", "Pearl Continental Lahore"}


def cleanup() -> None:
    db = SessionLocal()
    try:
        rows = db.query(Hotel).filter(
            (Hotel.property_id.in_(LEGACY_PROPERTY_IDS)) |
            (Hotel.name.in_(LEGACY_NAMES))
        ).all()
        if not rows:
            print("No legacy 600001/600002 hotel records found.")
            return

        hotel_ids = [hotel.id for hotel in rows]
        print(f"Found legacy hotel IDs: {hotel_ids}")

        from sqlalchemy import text
        tables = [
            "room_inventory", "room_availability", "room_rates", "rooms",
            "hotel_images", "hotel_amenities", "hotel_facilities",
        ]
        for table in tables:
            try:
                result = db.execute(
                    text(f"DELETE FROM {table} WHERE hotel_id = ANY(:ids)"),
                    {"ids": hotel_ids},
                )
                print(f"{table}: removed {result.rowcount}")
            except Exception as exc:
                db.rollback()
                print(f"{table}: skipped ({exc.__class__.__name__})")

        rows = db.query(Hotel).filter(Hotel.id.in_(hotel_ids)).all()
        for hotel in rows:
            print(f"Removing legacy hotel: id={hotel.id} property_id={hotel.property_id} name={hotel.name}")
            db.delete(hotel)
        db.commit()
        print(f"Removed {len(rows)} legacy hotel record(s).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cleanup()
