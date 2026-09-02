"""add structured property operational fields

Revision ID: 20260824_property_operational
Revises: 20260822_property_id
"""

from alembic import op
import sqlalchemy as sa

revision = "20260824_property_operational"
down_revision = "20260822_property_id"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {c["name"] for c in inspector.get_columns("hotels")}
    additions = {
        "payment_methods": sa.Column("payment_methods", sa.JSON(), nullable=False, server_default="[]"),
        "parking_floors": sa.Column("parking_floors", sa.JSON(), nullable=False, server_default="[]"),
        "breakfast_options": sa.Column("breakfast_options", sa.JSON(), nullable=False, server_default="[]"),
        "breakfast_other": sa.Column("breakfast_other", sa.Text(), nullable=True),
        "property_highlight_floors": sa.Column("property_highlight_floors", sa.JSON(), nullable=False, server_default="[]"),
    }
    for name, column in additions.items():
        if name not in columns:
            op.add_column("hotels", column)


def downgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {c["name"] for c in inspector.get_columns("hotels")}
    for name in ("property_highlight_floors", "breakfast_other", "breakfast_options", "parking_floors", "payment_methods"):
        if name in columns:
            op.drop_column("hotels", name)
