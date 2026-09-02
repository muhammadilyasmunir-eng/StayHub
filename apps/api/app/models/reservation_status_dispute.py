from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReservationDisputeStatus(str, Enum):
    OPEN = "Open"
    RESOLVED_GUEST = "Resolved - Guest Correct"
    REJECTED = "Rejected"


class ReservationStatusDispute(Base):
    __tablename__ = "reservation_status_disputes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    guest_id: Mapped[int] = mapped_column(
        ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    original_status: Mapped[str] = mapped_column(Text, nullable=False)
    guest_reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReservationDisputeStatus] = mapped_column(
        SqlEnum(ReservationDisputeStatus),
        default=ReservationDisputeStatus.OPEN,
        nullable=False,
        index=True,
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reservation = relationship("Reservation")
    guest = relationship("Guest")
    admin = relationship("User")
