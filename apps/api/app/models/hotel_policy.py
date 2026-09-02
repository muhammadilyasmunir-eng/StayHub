from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HotelPolicy(Base):
    __tablename__ = "hotel_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    child_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    pet_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    smoking_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_methods: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_bed_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    age_restriction: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quiet_hours: Mapped[str | None] = mapped_column(String(100), nullable=True)
    house_rules: Mapped[str | None] = mapped_column(Text, nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="policy")
