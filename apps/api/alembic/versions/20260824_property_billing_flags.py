"""add property billing and duplicate rejection flags

Revision ID: 20260824_property_flags
Revises: 20260824_property_operational
"""
from alembic import op
import sqlalchemy as sa
revision="20260824_property_flags"
down_revision="20260824_property_operational"
branch_labels=None
depends_on=None

def upgrade():
    inspector=sa.inspect(op.get_bind()); columns={c["name"] for c in inspector.get_columns("hotels")}
    if "invoice_overdue" not in columns: op.add_column("hotels",sa.Column("invoice_overdue",sa.Boolean(),nullable=False,server_default=sa.false()))
    if "duplicate_rejection" not in columns: op.add_column("hotels",sa.Column("duplicate_rejection",sa.Boolean(),nullable=False,server_default=sa.false()))
    indexes={i["name"] for i in inspector.get_indexes("hotels")}
    if "ix_hotels_invoice_overdue" not in indexes: op.create_index("ix_hotels_invoice_overdue","hotels",["invoice_overdue"],unique=False)
    if "ix_hotels_duplicate_rejection" not in indexes: op.create_index("ix_hotels_duplicate_rejection","hotels",["duplicate_rejection"],unique=False)

def downgrade():
    inspector=sa.inspect(op.get_bind()); indexes={i["name"] for i in inspector.get_indexes("hotels")}
    if "ix_hotels_duplicate_rejection" in indexes: op.drop_index("ix_hotels_duplicate_rejection",table_name="hotels")
    if "ix_hotels_invoice_overdue" in indexes: op.drop_index("ix_hotels_invoice_overdue",table_name="hotels")
    columns={c["name"] for c in inspector.get_columns("hotels")}
    if "duplicate_rejection" in columns: op.drop_column("hotels","duplicate_rejection")
    if "invoice_overdue" in columns: op.drop_column("hotels","invoice_overdue")
