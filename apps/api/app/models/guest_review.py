from datetime import date, datetime, timedelta

from sqlalchemy import Boolean, DateTime, Date, Float, ForeignKey, Integer, Text, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GuestReview(Base):
    __tablename__ = "guest_reviews"
    __table_args__ = (UniqueConstraint("reservation_id", name="uq_guest_review_reservation"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    staff_score: Mapped[float] = mapped_column(Float, nullable=False)
    facilities_score: Mapped[float] = mapped_column(Float, nullable=False)
    cleanliness_score: Mapped[float] = mapped_column(Float, nullable=False)
    comfort_score: Mapped[float] = mapped_column(Float, nullable=False)
    value_score: Mapped[float] = mapped_column(Float, nullable=False)
    location_score: Mapped[float] = mapped_column(Float, nullable=False)
    wifi_score: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    owner_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reservation = relationship("Reservation")
    hotel = relationship("Hotel")
    guest = relationship("Guest")
    customer = relationship("User", foreign_keys=[customer_user_id])

    @property
    def edit_deadline(self):
        return self.created_at + timedelta(days=7) if self.created_at else None
