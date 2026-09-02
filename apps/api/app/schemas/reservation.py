from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class BookingSource(str, Enum):
    WALK_IN = "WALK_IN"
    BOOKING_COM = "BOOKING_COM"
    AGODA = "AGODA"
    EXPEDIA = "EXPEDIA"
    AIRBNB = "AIRBNB"
    WEBSITE = "WEBSITE"
    PHONE = "PHONE"
    CORPORATE = "CORPORATE"
    TRAVEL_AGENT = "TRAVEL_AGENT"
    OTHER = "OTHER"


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class ReservationCreate(BaseModel):
    guest_id: int
    room_id: int
    booking_source: BookingSource = BookingSource.WALK_IN
    check_in: date
    check_out: date
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    room_rate: Decimal = Field(default=0)
    discount: Decimal = Field(default=0)
    tax: Decimal = Field(default=0)
    remarks: str | None = None


class ReservationUpdate(BaseModel):
    booking_source: BookingSource | None = None
    check_in: date | None = None
    check_out: date | None = None
    adults: int | None = Field(default=None, ge=1)
    children: int | None = Field(default=None, ge=0)
    room_rate: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    status: ReservationStatus | None = None
    payment_method: str | None = Field(default=None, pattern="^(pay_at_property|card|usdt)$")
    payment_status: str | None = None
    payment_reference: str | None = None
    remarks: str | None = None


class ReservationDateModification(BaseModel):
    check_in: date
    check_out: date


class ReservationNoShowRequest(BaseModel):
    waive_fee: bool


class ReservationResponse(BaseModel):
    id: int
    hotel_id: int
    guest_id: int
    room_id: int
    confirmation_no: str
    booking_source: BookingSource
    check_in: date
    check_out: date
    adults: int
    children: int
    room_rate: Decimal
    discount: Decimal
    tax: Decimal
    total_amount: Decimal
    payment_method: str
    payment_status: str
    payment_reference: str | None
    card_last4: str | None
    status: ReservationStatus
    remarks: str | None
    model_config = ConfigDict(from_attributes=True)
