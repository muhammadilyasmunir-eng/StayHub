"""add owner verification and signed agreement fields

Revision ID: 20260827_owner_verification
Revises: 20260827_three_approval_documents
"""
from alembic import op
import sqlalchemy as sa

revision = "20260827_owner_verification"
down_revision = "20260827_three_approval_documents"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("hotels")}
    if "owner_cnic_front_url" not in columns:
        op.add_column("hotels", sa.Column("owner_cnic_front_url", sa.String(length=1000), nullable=True))
    if "owner_cnic_back_url" not in columns:
        op.add_column("hotels", sa.Column("owner_cnic_back_url", sa.String(length=1000), nullable=True))
    if "signed_agreement_url" not in columns:
        op.add_column("hotels", sa.Column("signed_agreement_url", sa.String(length=1000), nullable=True))
    if "agreement_submitted_at" not in columns:
        op.add_column("hotels", sa.Column("agreement_submitted_at", sa.DateTime(timezone=True), nullable=True))
    if "owner_documents_submitted" not in columns:
        op.add_column("hotels", sa.Column("owner_documents_submitted", sa.Boolean(), nullable=False, server_default=sa.false()))
    inspector = sa.inspect(bind)
    indexes = {i.get("name") for i in inspector.get_indexes("hotels")}
    if "ix_hotels_owner_documents_submitted" not in indexes:
        op.create_index("ix_hotels_owner_documents_submitted", "hotels", ["owner_documents_submitted"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {i.get("name") for i in inspector.get_indexes("hotels")}
    if "ix_hotels_owner_documents_submitted" in indexes:
        op.drop_index("ix_hotels_owner_documents_submitted", table_name="hotels")
    columns = {c["name"] for c in inspector.get_columns("hotels")}
    for name in ("owner_documents_submitted", "agreement_submitted_at", "signed_agreement_url", "owner_cnic_back_url", "owner_cnic_front_url"):
        if name in columns:
            op.drop_column("hotels", name)
