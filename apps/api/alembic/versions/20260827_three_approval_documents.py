"""add document type to approval terms
Revision ID: 20260827_three_approval_documents
Revises: 20260827_terms_acceptance
"""
from alembic import op
import sqlalchemy as sa

revision = "20260827_three_approval_documents"
down_revision = "20260827_terms_acceptance"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("terms_documents")}
    if "document_type" not in columns:
        op.add_column("terms_documents", sa.Column("document_type", sa.String(40), nullable=True))
    op.execute("UPDATE terms_documents SET document_type='terms' WHERE document_type IS NULL")
    # Keep the database default aligned with the model without trying to recreate
    # an already-existing column/default from the application startup compatibility hook.
    op.alter_column("terms_documents", "document_type", nullable=False, server_default="terms")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("terms_documents")}
    if "document_type" in columns:
        op.drop_column("terms_documents", "document_type")
