from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoomType(Base):
    __tablename__ = "room_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    number_of_rooms: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_adults: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    max_children: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bed_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    room_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    smoking_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra_bed_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra_bed_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    extra_bed_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="room_types")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="room_type", cascade="all, delete-orphan")
    facilities: Mapped[list["RoomTypeFacility"]] = relationship("RoomTypeFacility", back_populates="room_type", cascade="all, delete-orphan")
    photos: Mapped[list["RoomTypePhoto"]] = relationship("RoomTypePhoto", back_populates="room_type", cascade="all, delete-orphan")
