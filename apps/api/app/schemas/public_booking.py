from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PublicBookingCreate(BaseModel):
    room_type_id: int
    check_in: date
    check_out: date
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str
    otp_token: str | None = None
    phone: str = Field(min_length=3, max_length=50)
    nationality: str = "Pakistan"
    address: str = "Online booking"
    city: str = ""
    country: str = "Pakistan"
    id_number: str = "STAYHUB-GUEST"
    payment_method: str = Field(default="pay_at_property", pattern="^(pay_at_property|card|usdt)$")
    payment_reference: str | None = Field(default=None, max_length=100)
    card_last4: str | None = Field(default=None, min_length=4, max_length=4, pattern="^[0-9]{4}$")


class PublicBookingDailyRate(BaseModel):
    date: date
    base_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    selling_price: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    total_price: Decimal


class PublicBookingResponse(BaseModel):
    confirmation_no: str
    reservation_id: int
    status: str
    hotel_id: int
    room_type_id: int
    room_name: str
    check_in: date
    check_out: date
    nights: int
    base_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    selling_price: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    daily_rates: list[PublicBookingDailyRate] = Field(default_factory=list)
    commission_percent: Decimal
    commission_amount: Decimal
    owner_amount: Decimal
    payment_method: str
    payment_status: str


class PublicPaymentOptionsResponse(BaseModel):
    methods: list[str]
    usdt_wallet_address: str
    usdt_network: str
