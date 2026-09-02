"""create reservations table

Revision ID: bcc6387baf5c
Revises: 9f50ee8996a6
Create Date: 2026-08-07 10:58:01.308888

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bcc6387baf5c"
down_revision: Union[str, Sequence[str], None] = "9f50ee8996a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("guest_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("confirmation_no", sa.String(length=50), nullable=False),
        sa.Column(
            "booking_source",
            sa.Enum(
                "WALK_IN",
                "BOOKING_COM",
                "AGODA",
                "EXPEDIA",
                "AIRBNB",
                "WEBSITE",
                "PHONE",
                "CORPORATE",
                "TRAVEL_AGENT",
                "OTHER",
                name="bookingsource",
            ),
            nullable=False,
        ),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("adults", sa.Integer(), nullable=False),
        sa.Column("children", sa.Integer(), nullable=False),
        sa.Column("room_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "CONFIRMED",
                "CHECKED_IN",
                "CHECKED_OUT",
                "CANCELLED",
                "NO_SHOW",
                name="reservationstatus",
            ),
            nullable=False,
        ),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["hotel_id"],
            ["hotels.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["guest_id"],
            ["guests.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["room_id"],
            ["rooms.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_reservations_id"),
        "reservations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_reservations_confirmation_no"),
        "reservations",
        ["confirmation_no"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_reservations_confirmation_no"),
        table_name="reservations",
    )

    op.drop_index(
        op.f("ix_reservations_id"),
        table_name="reservations",
    )

    op.drop_table("reservations")