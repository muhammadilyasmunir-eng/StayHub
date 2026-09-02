"""add property tax and room discount

Revision ID: 8c3f2d1a7b90
Revises: 7d2a1f9c4e61
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8c3f2d1a7b90"
down_revision: Union[str, Sequence[str], None] = "7d2a1f9c4e61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    hotel_columns = {c["name"] for c in inspector.get_columns("hotels")}
    if "tax_percent" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column("tax_percent", sa.Numeric(5, 2), server_default=sa.text("0"), nullable=False),
        )

    room_type_columns = {c["name"] for c in inspector.get_columns("room_types")}
    if "discount_percent" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column("discount_percent", sa.Numeric(5, 2), server_default=sa.text("0"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    room_type_columns = {c["name"] for c in inspector.get_columns("room_types")}
    if "discount_percent" in room_type_columns:
        op.drop_column("room_types", "discount_percent")

    hotel_columns = {c["name"] for c in inspector.get_columns("hotels")}
    if "tax_percent" in hotel_columns:
        op.drop_column("hotels", "tax_percent")
