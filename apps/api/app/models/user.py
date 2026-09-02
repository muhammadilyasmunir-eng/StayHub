from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    HOTEL_OWNER = "hotel_owner"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.CUSTOMER, nullable=False)

    # Never delete a property merely because an owner/user record is removed.
    # Property ownership is nullable and the DB FK uses SET NULL.
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel",
        foreign_keys="Hotel.owner_id",
        back_populates="owner",
        cascade="save-update, merge",
    )
