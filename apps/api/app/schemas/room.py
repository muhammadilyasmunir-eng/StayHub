from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RoomStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    DIRTY = "Dirty"
    CLEANING = "Cleaning"
    MAINTENANCE = "Maintenance"
    OUT_OF_ORDER = "Out of Order"


class RoomBase(BaseModel):
    room_number: str = Field(
        min_length=1,
        max_length=20,
    )

    floor: int = Field(
        ge=0,
    )

    smoking: bool = False

    active: bool = True

    status: RoomStatus = RoomStatus.AVAILABLE


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    floor: int | None = Field(
        default=None,
        ge=0,
    )

    smoking: bool | None = None

    active: bool | None = None

    status: RoomStatus | None = None


class RoomResponse(RoomBase):
    id: int
    room_type_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )