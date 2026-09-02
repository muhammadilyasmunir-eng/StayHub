from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoomTypeFacility(Base):
    __tablename__ = "room_type_facilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    room_type_id: Mapped[int] = mapped_column(
        ForeignKey("room_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    room_type: Mapped["RoomType"] = relationship(
        "RoomType",
        back_populates="facilities",
    )
