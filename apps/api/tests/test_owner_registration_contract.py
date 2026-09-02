import pytest
from pydantic import ValidationError

from app.schemas.user import OwnerRegistration, RegistrationDocument, RegistrationPhoto, RegistrationRoomType


def valid_registration(**overrides):
    data = {
        "full_name": "Test Owner",
        "email": "owner@example.com",
        "phone": "+923001234567",
        "username": "testowner",
        "password": "password123",
        "password_confirmation": "password123",
        "hotel_name": "Test Hotel",
        "hotel_slug": "test-hotel",
        "property_type": "Hotel",
        "description": "A test property",
        "star_rating": 4,
        "hotel_email": "hotel@example.com",
        "hotel_phone": "+92421234567",
        "country": "Pakistan",
        "city": "Lahore",
        "address": "1 Test Street",
        "postal_code": "54000",
        "total_rooms": 10,
        "check_in_time": "14:00",
        "check_out_time": "12:00",
        "amenities": ["Free WiFi"],
        "cancellation_policy": "Free cancellation before 24 hours.",
        "child_policy": "Children welcome.",
        "pet_policy": "Pets not allowed.",
        "smoking_policy": "Non-smoking property.",
        "payment_methods": "Cash, cards",
        "extra_bed_policy": "Extra beds available on request.",
        "age_restriction": "18+",
        "quiet_hours": "22:00-07:00",
        "photos": [
            RegistrationPhoto(photo_url="/uploads/hotel.jpg", is_primary=True, sort_order=0)
        ],
        "room_types": [
            RegistrationRoomType(
                name="Deluxe King",
                description="Deluxe room",
                number_of_rooms=2,
                max_adults=2,
                max_children=1,
                bed_type="King Bed",
                room_size="25 sqm",
                base_price=15000,
                smoking_allowed=False,
                extra_bed_available=True,
                extra_bed_price=3000,
                extra_bed_information="One extra bed on request.",
                facilities=[{"name": "TV", "available": True}],
                photos=[{"photo_url": "/uploads/room.jpg", "is_primary": True}],
            )
        ],
        "documents": [
            RegistrationDocument(
                document_type="Hotel License",
                license_number="123456",
                registration_number="REG-123",
                document_number="DOC-123",
                document_url="/uploads/license.pdf",
            )
        ],
    }
    data.update(overrides)
    return OwnerRegistration(**data)


def test_registration_requires_owner_phone_and_username():
    with pytest.raises(ValidationError):
        valid_registration(phone="")
    with pytest.raises(ValidationError):
        valid_registration(username="ab")


def test_registration_accepts_complete_policy_document_and_room_fields():
    registration = valid_registration()
    assert registration.smoking_policy == "Non-smoking property."
    assert registration.payment_methods == "Cash, cards"
    assert registration.room_types[0].extra_bed_available is True
    assert registration.room_types[0].extra_bed_price == 3000
    assert registration.documents[0].license_number == "123456"
    assert registration.documents[0].registration_number == "REG-123"


def test_registration_requires_at_least_one_primary_hotel_photo():
    with pytest.raises(ValueError, match="primary hotel photo"):
        valid_registration(photos=[RegistrationPhoto(photo_url="/uploads/hotel.jpg")])


def test_registration_rejects_room_without_photo_or_facility():
    with pytest.raises(ValueError, match="room type"):
        valid_registration(room_types=[{"name": "Basic", "photos": [], "facilities": []}])


def test_registration_rejects_short_or_non_numeric_property_license():
    with pytest.raises(ValueError, match="licence number"):
        valid_registration(documents=[RegistrationDocument(document_type="Hotel License", license_number="12345", document_url="/uploads/license.pdf")])
    with pytest.raises(ValueError, match="licence number"):
        valid_registration(documents=[RegistrationDocument(document_type="Hotel License", license_number="ABC123", document_url="/uploads/license.pdf")])
