"""allow OTHER guest identification type

Revision ID: 20260829_add_other_idtype
Revises: 20260828_room_availability_calendar
"""
from alembic import op

revision = "20260829_add_other_idtype"
down_revision = "20260828_room_availability_calendar"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Guest.IDType supports OTHER, but the original database enum did not.
    # SQLAlchemy persists Python enum member names, so add the exact value.
    op.execute("ALTER TYPE idtype ADD VALUE IF NOT EXISTS 'OTHER'")


def downgrade() -> None:
    # PostgreSQL does not safely support removing an enum value in place.
    pass
