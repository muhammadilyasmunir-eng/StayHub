"""add awaiting_terms to hotelstatus enum

Revision ID: 20260828_add_awaiting_terms_status
Revises: 20260827_owner_verification
"""
from alembic import op

revision = "20260828_add_awaiting_terms_status"
down_revision = "20260827_owner_verification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL enum values are case-sensitive. SQLAlchemy's HotelStatus enum
    # persists the Python enum member name (AWAITING_TERMS), so add that exact
    # value to the existing hotelstatus type.
    op.execute("ALTER TYPE hotelstatus ADD VALUE IF NOT EXISTS 'AWAITING_TERMS'")


def downgrade() -> None:
    # PostgreSQL does not support removing an enum value directly. The value is
    # intentionally retained on downgrade to avoid unsafe data/type rewrites.
    pass
