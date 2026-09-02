from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.guest import Gender, IDType


class GuestBase(BaseModel):
    first_name: str
    last_name: str
    gender: Gender

    date_of_birth: Optional[date] = None

    nationality: str

    id_type: IDType
    id_number: str

    phone: str
    email: Optional[EmailStr] = None

    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    vip: bool = False
    blacklist: bool = False

    notes: Optional[str] = None


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    id_type: Optional[IDType] = None
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    vip: Optional[bool] = None
    blacklist: Optional[bool] = None
    notes: Optional[str] = None


class GuestResponse(GuestBase):
    id: int
    hotel_id: int

    model_config = ConfigDict(from_attributes=True)