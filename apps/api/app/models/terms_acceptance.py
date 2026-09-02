from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TermsDocument(Base):
    __tablename__ = "terms_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False, default="terms")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)


class HotelTermsAcceptance(Base):
    __tablename__ = "hotel_terms_acceptances"
    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    terms_document_id: Mapped[int] = mapped_column(ForeignKey("terms_documents.id", ondelete="RESTRICT"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel")
    terms_document: Mapped[TermsDocument] = relationship("TermsDocument")
    owner: Mapped["User"] = relationship("User")
