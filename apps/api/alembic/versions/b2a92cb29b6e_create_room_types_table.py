"""create room_types table

Revision ID: b2a92cb29b6e
Revises: 7c91a4f2b8d3
Create Date: 2026-08-06 17:51:04.832029

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2a92cb29b6e"
down_revision: Union[str, Sequence[str], None] = "7c91a4f2b8d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "room_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_adults", sa.Integer(), nullable=False),
        sa.Column("max_children", sa.Integer(), nullable=False),
        sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.Boolean(), nullable=False),
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
        op.f("ix_room_types_id"),
        "room_types",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_room_types_id"),
        table_name="room_types",
    )

    op.drop_table("room_types")