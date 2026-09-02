from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReservationCommission(Base):
    __tablename__ = "reservation_commissions"
    __table_args__ = (UniqueConstraint("reservation_id", name="uq_reservation_commission_reservation"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True)
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    commissionable_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    owner_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="commission")
