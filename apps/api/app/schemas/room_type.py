from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class RoomTypeBase(BaseModel):
    name: str
    description: str | None = None
    number_of_rooms: int = Field(default=1, ge=1)
    max_adults: int = 2
    max_children: int = 0
    base_price: Decimal = Decimal("0.00")
    discount_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    status: bool = True
    room_size: str | None = None


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    number_of_rooms: int | None = Field(default=None, ge=1)
    max_adults: int | None = None
    max_children: int | None = None
    base_price: Decimal | None = None
    discount_percent: Decimal | None = Field(default=None, ge=0, le=100)
    status: bool | None = None
    room_size: str | None = None


class RoomTypeResponse(RoomTypeBase):
    id: int
    hotel_id: int

    @computed_field
    @property
    def selling_price(self) -> Decimal:
        return (self.base_price * (Decimal("100") - self.discount_percent) / Decimal("100")).quantize(Decimal("0.01"))

    model_config = ConfigDict(from_attributes=True)
