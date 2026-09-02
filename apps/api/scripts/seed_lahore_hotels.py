"""Idempotently seed the five requested Lahore hotel-owner test properties.

Run from apps/api with the project's Python environment, for example:
    python scripts/seed_lahore_hotels.py

These records are intentionally created as PENDING. No verification document is
represented as approved; the document rows only satisfy the current data model
for seeded review records.
"""

from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.hotel import Hotel, HotelStatus
from app.models.hotel_document import HotelDocument
from app.models.hotel_facility import HotelFacility
from app.models.hotel_photo import HotelPhoto
from app.models.hotel_policy import HotelPolicy
from app.models.room_type import RoomType
from app.models.room_type_facility import RoomTypeFacility
from app.models.user import User, UserRole

PASSWORD = "12345678"

HOTELS = [
    {
        "name": "HOTEL dGATES Lahore",
        "email": "muhammadilyasmunir@gmail.com",
        "username": "dGATES_Lahore",
        "rates": [15000, 16000, 17000],
        "property_id": "9000000001",
        "slug": "hotel-dgates-lahore",
        "phone": "+924235700000",
        "address": "Lahore, Punjab, Pakistan",
    },
    {
        "name": "Best Western Premier Hotel Gulberg Lahore",
        "email": "muhammadilyasmunir01@gmail.com",
        "username": "BW_Gulberg_Lahore",
        "rates": [18000, 19000, 20000],
        "property_id": "9000000002",
        "slug": "best-western-premier-hotel-gulberg-lahore",
        "phone": "+924235700001",
        "address": "Gulberg, Lahore, Punjab, Pakistan",
    },
    {
        "name": "Avari Lahore Hotel Lahore",
        "email": "muhammadilyasmunir02@gmail.com",
        "username": "Avari_Lahore",
        "rates": [15500, 16500, 17500],
        "property_id": "9000000003",
        "slug": "avari-lahore-hotel",
        "phone": "+924235700002",
        "address": "Lahore, Punjab, Pakistan",
    },
    {
        "name": "Pearl Continental Hotel, Lahore",
        "email": "muhammadilyasmunir03@gmail.com",
        "username": "PC_Lahore",
        "rates": [18500, 19500, 20500],
        "property_id": "9000000004",
        "slug": "pearl-continental-hotel-lahore",
        "phone": "+924235700003",
        "address": "Lahore, Punjab, Pakistan",
    },
    {
        "name": "Indigo Heights Hotel and Suites, Gulberg Lahore",
        "email": "muhammadilyasmunir04@gmail.com",
        "username": "Indigo_Heights_Lahore",
        "rates": [21000, 22000, 23000],
        "property_id": "9000000005",
        "slug": "indigo-heights-hotel-suites-gulberg-lahore",
        "phone": "+924235700004",
        "address": "Gulberg, Lahore, Punjab, Pakistan",
    },
]

ROOMS = ["Deluxe Master", "Deluxe Twin", "Suite"]


def seed():
    db = SessionLocal()
    try:
        for item in HOTELS:
            owner = db.query(User).filter(User.email == item["email"]).first()
            if owner is None:
                owner = User(
                    email=item["email"],
                    full_name=item["name"],
                    username=item["username"],
                    hashed_password=hash_password(PASSWORD),
                    role=UserRole.HOTEL_OWNER,
                )
                db.add(owner)
                db.flush()
            else:
                owner.role = UserRole.HOTEL_OWNER
                owner.hashed_password = hash_password(PASSWORD)
                owner.username = owner.username or item["username"]

            hotel = db.query(Hotel).filter(Hotel.property_id == item["property_id"]).first()
            if hotel is None:
                hotel = Hotel(
                    owner_id=owner.id,
                    property_id=item["property_id"],
                    name=item["name"],
                    slug=item["slug"],
                    property_type="Hotel",
                    description=f"Seeded StayHub review property for {item['name']}.",
                    star_rating=None,
                    email=item["email"],
                    phone=item["phone"],
                    country="Pakistan",
                    city="Lahore",
                    address=item["address"],
                    postal_code="54000",
                    total_rooms=30,
                    check_in_time="14:00",
                    check_out_time="12:00",
                    timezone="Asia/Karachi",
                    currency="PKR",
                    tax_percent=0,
                    status=HotelStatus.PENDING,
                )
                db.add(hotel)
                db.flush()
            else:
                hotel.owner_id = owner.id
                hotel.status = HotelStatus.PENDING
                hotel.total_rooms = 30

            # Keep seeded review data complete enough for the existing admin model.
            if not db.query(HotelFacility).filter(HotelFacility.hotel_id == hotel.id).first():
                for name in ["Wi-Fi", "Parking", "24-hour Front Desk", "Air Conditioning"]:
                    db.add(HotelFacility(hotel_id=hotel.id, name=name, available=True))

            if not db.query(HotelPhoto).filter(HotelPhoto.hotel_id == hotel.id).first():
                db.add(HotelPhoto(
                    hotel_id=hotel.id,
                    photo_url="/static/images/property-placeholder.svg",
                    caption="Building photo pending owner/admin upload",
                    category="building",
                    is_primary=True,
                    sort_order=0,
                ))

            if not db.query(HotelPolicy).filter(HotelPolicy.hotel_id == hotel.id).first():
                db.add(HotelPolicy(
                    hotel_id=hotel.id,
                    cancellation_policy="Pending admin review",
                    child_policy="Pending admin review",
                    pet_policy="Pending admin review",
                    smoking_policy="Pending admin review",
                    payment_methods="Pending admin review",
                ))

            if not db.query(HotelDocument).filter(HotelDocument.hotel_id == hotel.id).first():
                db.add(HotelDocument(
                    hotel_id=hotel.id,
                    document_type="seed-review-record",
                    license_number=item["property_id"],
                    document_url="",
                    status="pending",
                    admin_notes="Seeded review record; replace with actual verification document before approval.",
                ))

            existing_rooms = {
                room.name: room
                for room in db.query(RoomType).filter(RoomType.hotel_id == hotel.id).all()
            }
            for room_name, rate in zip(ROOMS, item["rates"]):
                room = existing_rooms.get(room_name)
                if room is None:
                    room = RoomType(
                        hotel_id=hotel.id,
                        name=room_name,
                        description=f"{room_name} at {item['name']}",
                        number_of_rooms=10,
                        max_adults=2,
                        max_children=0,
                        base_price=Decimal(rate),
                        status=True,
                    )
                    db.add(room)
                    db.flush()
                else:
                    room.number_of_rooms = 10
                    room.max_adults = 2
                    room.base_price = Decimal(rate)
                    room.status = True

                if not db.query(RoomTypeFacility).filter(RoomTypeFacility.room_type_id == room.id).first():
                    for facility in ["Wi-Fi", "Air Conditioning", "Private Bathroom"]:
                        db.add(RoomTypeFacility(room_type_id=room.id, name=facility, available=True))

        db.commit()
        print("Seed complete: 5 Lahore hotels are PENDING with 3 room types each.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
