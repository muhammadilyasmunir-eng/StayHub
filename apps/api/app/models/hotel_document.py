from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HotelDocument(Base):
    __tablename__ = "hotel_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    license_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="documents")
