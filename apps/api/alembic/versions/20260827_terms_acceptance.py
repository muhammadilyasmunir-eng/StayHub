"""add versioned terms, acceptance and owner notifications
Revision ID: 20260827_terms_acceptance
Revises: 20260824_property_flags
"""
from alembic import op
import sqlalchemy as sa

revision = "20260827_terms_acceptance"
down_revision = "20260824_property_flags"
branch_labels = None
depends_on = None


def _has_table(inspector, name):
    return name in inspector.get_table_names()


def _has_index(inspector, table, name):
    return any(i.get("name") == name for i in inspector.get_indexes(table))


def upgrade():
    # Newer revision ids are longer than the original Alembic default in this
    # database. Widen it before Alembic attempts to write the next revision id.
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64)")

    # The application uses SQLAlchemy create_all on startup, so these tables can
    # already exist before Alembic reaches this revision. Never recreate them.
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "terms_documents"):
        op.create_table(
            "terms_documents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("version", sa.String(50), nullable=False, unique=True),
            sa.Column("file_name", sa.String(255), nullable=False),
            sa.Column("file_url", sa.String(1000), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )

    inspector = sa.inspect(bind)
    if not _has_table(inspector, "hotel_terms_acceptances"):
        op.create_table(
            "hotel_terms_acceptances",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False),
            sa.Column("terms_document_id", sa.Integer(), sa.ForeignKey("terms_documents.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("accepted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("ip_address", sa.String(64), nullable=True),
            sa.Column("user_agent", sa.String(1000), nullable=True),
        )

    inspector = sa.inspect(bind)
    if not _has_index(inspector, "hotel_terms_acceptances", "ix_hotel_terms_acceptances_hotel_id"):
        op.create_index("ix_hotel_terms_acceptances_hotel_id", "hotel_terms_acceptances", ["hotel_id"])

    inspector = sa.inspect(bind)
    if not _has_table(inspector, "notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=True),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("type", sa.String(50), nullable=False, server_default="general"),
            sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    inspector = sa.inspect(bind)
    if not _has_index(inspector, "notifications", "ix_notifications_user_id"):
        op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    if not _has_index(inspector, "notifications", "ix_notifications_hotel_id"):
        op.create_index("ix_notifications_hotel_id", "notifications", ["hotel_id"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _has_table(inspector, "notifications"):
        if _has_index(inspector, "notifications", "ix_notifications_hotel_id"):
            op.drop_index("ix_notifications_hotel_id", table_name="notifications")
        if _has_index(inspector, "notifications", "ix_notifications_user_id"):
            op.drop_index("ix_notifications_user_id", table_name="notifications")
        op.drop_table("notifications")
    inspector = sa.inspect(bind)
    if _has_table(inspector, "hotel_terms_acceptances"):
        if _has_index(inspector, "hotel_terms_acceptances", "ix_hotel_terms_acceptances_hotel_id"):
            op.drop_index("ix_hotel_terms_acceptances_hotel_id", table_name="hotel_terms_acceptances")
        op.drop_table("hotel_terms_acceptances")
    inspector = sa.inspect(bind)
    if _has_table(inspector, "terms_documents"):
        op.drop_table("terms_documents")
