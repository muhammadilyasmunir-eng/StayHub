"""add property-level tax and commission configuration

Revision ID: 20260829_property_billing_configuration
Revises: 20260829_add_other_idtype
"""
from alembic import op
import sqlalchemy as sa

revision = "20260829_property_billing_configuration"
down_revision = "20260829_add_other_idtype"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing 0.00 values were defaults, not an explicit admin configuration.
    # Clear them so every currently-live property must be configured once.
    op.execute("UPDATE hotels SET tax_percent = NULL WHERE tax_percent = 0")
    op.alter_column("hotels", "tax_percent", existing_type=sa.Numeric(5, 2), nullable=True, server_default=None)
    op.add_column("hotels", sa.Column("commission_percent", sa.Numeric(5, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("hotels", "commission_percent")
    op.execute("UPDATE hotels SET tax_percent = 0 WHERE tax_percent IS NULL")
    op.alter_column("hotels", "tax_percent", existing_type=sa.Numeric(5, 2), nullable=False, server_default="0")
