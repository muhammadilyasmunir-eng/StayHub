from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoomTypePhoto(Base):
    __tablename__ = "room_type_photos"

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

    photo_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    caption: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    room_type: Mapped["RoomType"] = relationship(
        "RoomType",
        back_populates="photos",
    )
