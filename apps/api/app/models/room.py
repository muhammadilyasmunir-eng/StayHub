from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


class RoomStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    DIRTY = "Dirty"
    CLEANING = "Cleaning"
    MAINTENANCE = "Maintenance"
    OUT_OF_ORDER = "Out of Order"


class Room(Base):
    __tablename__ = "rooms"

    # -----------------------------
    # Primary Key
    # -----------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # -----------------------------
    # Room Type
    # -----------------------------

    room_type_id: Mapped[int] = mapped_column(
        ForeignKey("room_types.id", ondelete="CASCADE"),
        nullable=False,
    )

    # -----------------------------
    # Room Information
    # -----------------------------

    room_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    floor: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    smoking: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -----------------------------
    # Room Status
    # -----------------------------

    status: Mapped[RoomStatus] = mapped_column(
        SqlEnum(RoomStatus),
        default=RoomStatus.AVAILABLE,
        nullable=False,
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

    room_type: Mapped["RoomType"] = relationship(
        "RoomType",
        back_populates="rooms",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="room",
        cascade="all, delete-orphan",
    )