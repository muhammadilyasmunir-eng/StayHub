"""create guests table

Revision ID: 9f50ee8996a6
Revises: 5788460f5284
Create Date: 2026-08-07 10:51:44.242015
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f50ee8996a6"
down_revision: Union[str, Sequence[str], None] = "5788460f5284"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "guests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("MALE", "FEMALE", "OTHER", name="gender"),
            nullable=False,
        ),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(length=100), nullable=False),
        sa.Column(
            "id_type",
            sa.Enum(
                "CNIC",
                "PASSPORT",
                "DRIVING_LICENSE",
                name="idtype",
            ),
            nullable=False,
        ),
        sa.Column("id_number", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("vip", sa.Boolean(), nullable=False),
        sa.Column("blacklist", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_guests_id"),
        "guests",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_guests_id"),
        table_name="guests",
    )

    op.drop_table("guests")