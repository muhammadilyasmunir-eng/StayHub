from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class IDType(str, Enum):
    CNIC = "CNIC"
    PASSPORT = "Passport"
    DRIVING_LICENSE = "Driving License"
    OTHER = "Other"


class Guest(Base):
    __tablename__ = "guests"

    # -----------------------------
    # Primary Key
    # -----------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # -----------------------------
    # Hotel
    # -----------------------------

    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # -----------------------------
    # Personal Information
    # -----------------------------

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    gender: Mapped[Gender] = mapped_column(
        SqlEnum(Gender),
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    nationality: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # -----------------------------
    # Identification
    # -----------------------------

    id_type: Mapped[IDType] = mapped_column(
        SqlEnum(IDType),
        nullable=False,
    )

    id_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # -----------------------------
    # Contact Information
    # -----------------------------

    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # -----------------------------
    # Guest Flags
    # -----------------------------

    vip: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    blacklist: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -----------------------------
    # Notes
    # -----------------------------

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -----------------------------
    # Timestamps
    # -----------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="guests",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="guest",
        cascade="all, delete-orphan",
    )