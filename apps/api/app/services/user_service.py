from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.hotel import Hotel, HotelStatus
from app.models.hotel_photo import HotelPhoto
from app.models.hotel_document import HotelDocument
from app.models.hotel_facility import HotelFacility
from app.models.hotel_policy import HotelPolicy
from app.models.room_type import RoomType
from app.models.room_type_photo import RoomTypePhoto
from app.models.room_type_facility import RoomTypeFacility
from app.models.room_availability import RoomAvailability
from app.schemas.user import UserCreate, OwnerRegistration
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str): return db.query(User).filter(User.email == email).first()
def get_user_by_login(db: Session, login: str): return db.query(User).filter((User.email == login) | (User.username == login)).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, full_name=user.full_name, hashed_password=hash_password(user.password), role=UserRole.CUSTOMER)
    db.add(db_user); db.commit(); db.refresh(db_user); return db_user

def authenticate_user(db: Session, email_or_username: str, password: str):
    user = get_user_by_login(db, email_or_username)
    if user is None or not verify_password(password, user.hashed_password): return None
    return user

def create_owner_registration(db: Session, registration: OwnerRegistration):
    if get_user_by_email(db, registration.email): raise ValueError("Owner email is already registered.")
    if db.query(User).filter(User.username == registration.username).first(): raise ValueError("Owner username is already registered.")
    if db.query(Hotel).filter(Hotel.email == registration.hotel_email).first(): raise ValueError("Hotel email already exists.")
    if db.query(Hotel).filter(Hotel.slug == registration.hotel_slug).first(): raise ValueError("Hotel slug already exists.")
    license_numbers = [d.license_number.strip() for d in registration.documents if d.license_number and d.license_number.strip()]
    if not license_numbers: raise ValueError("Hotel licence number is required and must be at least 6 digits.")
    property_id = license_numbers[0]
    if db.query(Hotel).filter(Hotel.property_id == property_id).first(): raise ValueError("Hotel licence number / Property ID already exists.")
    try:
        owner = User(email=registration.email, full_name=registration.full_name, phone=registration.phone, username=registration.username, hashed_password=hash_password(registration.password), role=UserRole.HOTEL_OWNER)
        db.add(owner); db.flush()
        hotel = Hotel(owner_id=owner.id, property_id=property_id, name=registration.hotel_name, slug=registration.hotel_slug, property_type=registration.property_type, description=registration.description, star_rating=registration.star_rating, email=registration.hotel_email, phone=registration.hotel_phone, alternate_phone=registration.alternate_phone, website=registration.website, country=registration.country, city=registration.city, address=registration.address, postal_code=registration.postal_code, latitude=registration.latitude, longitude=registration.longitude, total_rooms=registration.total_rooms, check_in_time=registration.check_in_time, check_out_time=registration.check_out_time, timezone=registration.timezone, currency=registration.currency, status=HotelStatus.PENDING, payment_methods=list(dict.fromkeys(registration.payment_methods_selected)), parking_floors=list(dict.fromkeys(registration.parking_floors)), breakfast_options=list(dict.fromkeys(registration.breakfast_options)), breakfast_other=registration.breakfast_other, property_highlight_floors=sorted(set(registration.property_highlight_floors)))
        db.add(hotel); db.flush()
        for facility_name in registration.amenities:
            if facility_name.strip(): db.add(HotelFacility(hotel_id=hotel.id, name=facility_name.strip(), available=True))
        db.add(HotelPolicy(hotel_id=hotel.id, cancellation_policy=registration.cancellation_policy, child_policy=registration.child_policy, pet_policy=registration.pet_policy, smoking_policy=registration.smoking_policy, payment_methods=registration.payment_methods, extra_bed_policy=registration.extra_bed_policy, age_restriction=registration.age_restriction, quiet_hours=registration.quiet_hours, house_rules=registration.house_rules))
        for photo_data in registration.photos: db.add(HotelPhoto(hotel_id=hotel.id, photo_url=photo_data.photo_url, caption=photo_data.caption, category=photo_data.category, is_primary=photo_data.is_primary, sort_order=photo_data.sort_order))
        for room_data in registration.room_types:
            room_type = RoomType(hotel_id=hotel.id, name=room_data.name, description=room_data.description, number_of_rooms=room_data.number_of_rooms, max_adults=room_data.max_adults, max_children=room_data.max_children, bed_type=room_data.bed_type, room_size=room_data.room_size, base_price=room_data.base_price, discount_percent=room_data.discount_percent, smoking_allowed=room_data.smoking_allowed, extra_bed_available=room_data.extra_bed_available, extra_bed_price=room_data.extra_bed_price, extra_bed_information=room_data.extra_bed_information, status=True)
            db.add(room_type); db.flush()
            for facility in room_data.facilities:
                if facility.name.strip(): db.add(RoomTypeFacility(room_type_id=room_type.id, name=facility.name.strip(), available=facility.available))
            for photo_data in room_data.photos: db.add(RoomTypePhoto(room_type_id=room_type.id, photo_url=photo_data.photo_url, caption=photo_data.caption, is_primary=photo_data.is_primary, sort_order=photo_data.sort_order))
            start=date.today()
            for offset in range(365):
                day=start+timedelta(days=offset)
                db.add(RoomAvailability(room_type_id=room_type.id,date=day,rooms_to_sell=room_type.number_of_rooms,rate=room_type.base_price,bookable=True))
        for document_data in registration.documents:
            db.add(HotelDocument(hotel_id=hotel.id, document_type=document_data.document_type, license_number=document_data.license_number, registration_number=document_data.registration_number, document_number=document_data.document_number, document_url=document_data.document_url, status="pending", admin_notes=document_data.admin_notes))
        db.commit(); db.refresh(owner); db.refresh(hotel); return owner, hotel
    except Exception:
        db.rollback(); raise
