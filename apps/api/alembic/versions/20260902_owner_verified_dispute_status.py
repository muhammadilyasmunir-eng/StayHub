"""add owner verified reservation dispute status

Revision ID: 20260902_owner_verified_dispute_status
Revises: 20260902_reservation_status_disputes
"""
from alembic import op

revision = "20260902_owner_verified_dispute_status"
down_revision = "20260902_reservation_status_disputes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        bind.exec_driver_sql(
            "ALTER TYPE reservationdisputestatus ADD VALUE IF NOT EXISTS 'OWNER_VERIFIED'"
        )


def downgrade() -> None:
    # PostgreSQL enum values cannot be removed safely in-place. Keeping the value
    # during downgrade avoids destructive data rewriting for existing disputes.
    pass
