from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReservationStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CHECKED_IN = "Checked In"
    CHECKED_OUT = "Checked Out"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


class BookingSource(str, Enum):
    WALK_IN = "Walk In"
    BOOKING_COM = "Booking.com"
    AGODA = "Agoda"
    EXPEDIA = "Expedia"
    AIRBNB = "Airbnb"
    WEBSITE = "Website"
    PHONE = "Phone"
    CORPORATE = "Corporate"
    TRAVEL_AGENT = "Travel Agent"
    OTHER = "Other"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id", ondelete="CASCADE"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)

    confirmation_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    booking_source: Mapped[BookingSource] = mapped_column(SqlEnum(BookingSource), default=BookingSource.WALK_IN, nullable=False)

    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    adults: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    children: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    room_rate: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    payment_method: Mapped[str] = mapped_column(String(30), default="pay_at_property", nullable=False)
    payment_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    payment_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    card_last4: Mapped[str | None] = mapped_column(String(4), nullable=True)

    status: Mapped[ReservationStatus] = mapped_column(SqlEnum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="reservations")
    guest: Mapped["Guest"] = relationship("Guest", back_populates="reservations")
    room: Mapped["Room"] = relationship("Room", back_populates="reservations")
    commission: Mapped["ReservationCommission | None"] = relationship("ReservationCommission", back_populates="reservation", uselist=False, cascade="all, delete-orphan")
