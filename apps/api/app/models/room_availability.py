from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoomAvailability(Base):
    __tablename__ = "room_availability"
    __table_args__ = (UniqueConstraint("room_type_id", "date", name="uq_room_availability_type_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    rooms_to_sell: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    room_type: Mapped["RoomType"] = relationship("RoomType")
