"""create rooms table

Revision ID: 5788460f5284
Revises: b2a92cb29b6e
Create Date: 2026-08-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5788460f5284"
down_revision: Union[str, Sequence[str], None] = "b2a92cb29b6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("room_type_id", sa.Integer(), nullable=False),
        sa.Column("room_number", sa.String(length=20), nullable=False),
        sa.Column("floor", sa.Integer(), nullable=False),
        sa.Column("smoking", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "AVAILABLE",
                "OCCUPIED",
                "RESERVED",
                "DIRTY",
                "CLEANING",
                "MAINTENANCE",
                "OUT_OF_ORDER",
                name="roomstatus",
            ),
            nullable=False,
        ),
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
            ["room_type_id"],
            ["room_types.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_rooms_id"),
        "rooms",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_rooms_id"),
        table_name="rooms",
    )

    op.drop_table("rooms")