from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RegistrationPhoto(BaseModel):
    photo_url: str
    caption: str | None = None
    category: str | None = None
    is_primary: bool = False
    sort_order: int = Field(default=0, ge=0)

class RegistrationDocument(BaseModel):
    document_type: str
    license_number: str | None = None
    registration_number: str | None = None
    document_number: str | None = None
    document_url: str
    admin_notes: str | None = None

class RegistrationRoomPhoto(BaseModel):
    photo_url: str
    caption: str | None = None
    is_primary: bool = False
    sort_order: int = Field(default=0, ge=0)

class RegistrationRoomFacility(BaseModel):
    name: str
    available: bool = True

class RegistrationRoomType(BaseModel):
    name: str
    description: str | None = None
    number_of_rooms: int = Field(default=1, ge=1)
    max_adults: int = Field(default=2, ge=1)
    max_children: int = Field(default=0, ge=0)
    bed_type: str | None = None
    room_size: str | None = None
    base_price: float = Field(default=0, ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    smoking_allowed: bool = False
    extra_bed_available: bool = False
    extra_bed_price: float | None = Field(default=None, ge=0)
    extra_bed_information: str | None = None
    facilities: list[RegistrationRoomFacility] = Field(default_factory=list)
    photos: list[RegistrationRoomPhoto] = Field(default_factory=list)

class OwnerRegistration(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=50)
    username: str = Field(min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8)
    password_confirmation: str = Field(min_length=8)
    hotel_name: str = Field(min_length=2, max_length=255)
    hotel_slug: str = Field(min_length=2, max_length=255, pattern=r"^[a-z0-9-]+$")
    property_type: str = "Hotel"
    description: str | None = None
    star_rating: float | None = Field(default=None, ge=0, le=5)
    hotel_email: EmailStr
    hotel_phone: str = Field(min_length=7, max_length=50)
    alternate_phone: str | None = None
    website: str | None = None
    country: str = Field(min_length=2)
    city: str = Field(min_length=2)
    address: str = Field(min_length=3)
    postal_code: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    total_rooms: int = Field(default=0, ge=0)
    check_in_time: str = "14:00"
    check_out_time: str = "12:00"
    timezone: str = "Asia/Karachi"
    currency: str = "PKR"
    amenities: list[str] = Field(default_factory=list)
    payment_methods_selected: list[str] = Field(default_factory=list)
    parking_floors: list[str | int] = Field(default_factory=list)
    breakfast_options: list[str] = Field(default_factory=list)
    breakfast_other: str | None = None
    property_highlight_floors: list[int] = Field(default_factory=list)
    cancellation_policy: str | None = None
    child_policy: str | None = None
    pet_policy: str | None = None
    smoking_policy: str | None = None
    payment_methods: str | None = None
    extra_bed_policy: str | None = None
    age_restriction: str | None = None
    quiet_hours: str | None = None
    house_rules: str | None = None
    photos: list[RegistrationPhoto] = Field(default_factory=list)
    room_types: list[RegistrationRoomType] = Field(default_factory=list)
    documents: list[RegistrationDocument] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_registration(self):
        if self.password != self.password_confirmation: raise ValueError("Password and password confirmation do not match.")
        if not self.hotel_name.strip() or not self.address.strip() or not self.country.strip() or not self.city.strip() or not self.hotel_phone.strip(): raise ValueError("Required property information is missing.")
        if not self.amenities: raise ValueError("At least one property facility is required.")
        if any(x not in {"Cash", "Credit Card", "Debit Card"} for x in self.payment_methods_selected): raise ValueError("Unsupported payment method")
        if any(x not in {"Continental", "American", "Asian", "Buffet", "Pakistani"} for x in self.breakfast_options): raise ValueError("Unsupported breakfast option")
        if any(x not in ("Ground", "Basement") and not (isinstance(x, int) and 1 <= x <= 200) for x in self.parking_floors): raise ValueError("Parking floor must be Ground, Basement, or 1-200")
        if any(not isinstance(x, int) or x < 1 or x > 200 for x in self.property_highlight_floors): raise ValueError("Property highlight floors must be 1-200")
        if not self.photos or sum(1 for photo in self.photos if photo.is_primary) != 1: raise ValueError("Exactly one primary hotel photo is required.")
        if not self.documents: raise ValueError("At least one verification document is required.")
        license_numbers = [d.license_number.strip() for d in self.documents if d.license_number and d.license_number.strip()]
        if not license_numbers or any(not number.isdigit() or len(number) < 6 for number in license_numbers): raise ValueError("Hotel licence number must contain at least 6 digits.")
        if not self.room_types: raise ValueError("At least one room type is required.")
        for room in self.room_types:
            if len(room.photos) < 3 or len(room.photos) > 10: raise ValueError(f"room type '{room.name}' needs a minimum of 3 and maximum of 10 photos.")
            if not room.facilities or sum(1 for photo in room.photos if photo.is_primary) != 1: raise ValueError(f"room type '{room.name}' needs facilities and exactly one primary photo.")
            if room.extra_bed_available and room.extra_bed_price is None and not room.extra_bed_information: raise ValueError(f"room type '{room.name}' needs extra-bed price or information.")
        return self

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None = None
    username: str | None = None
    role: UserRole
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
