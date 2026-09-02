"""add reservation status disputes and notifications

Revision ID: 20260902_reservation_status_disputes
Revises: 20260829_property_billing_configuration
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260902_reservation_status_disputes"
down_revision = "20260829_property_billing_configuration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("type", sa.String(length=50), nullable=False, server_default="general"),
            sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
        op.create_index("ix_notifications_hotel_id", "notifications", ["hotel_id"])

    dispute_status = sa.Enum("OPEN", "RESOLVED_GUEST", "REJECTED", name="reservationdisputestatus")
    dispute_status.create(bind, checkfirst=True)
    if not inspector.has_table("reservation_status_disputes"):
        op.create_table(
            "reservation_status_disputes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reservation_id", sa.Integer(), sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("guest_id", sa.Integer(), sa.ForeignKey("guests.id", ondelete="CASCADE"), nullable=False),
            sa.Column("original_status", sa.Text(), nullable=False),
            sa.Column("guest_reason", sa.Text(), nullable=False),
            sa.Column("status", dispute_status, nullable=False, server_default="OPEN"),
            sa.Column("admin_note", sa.Text(), nullable=True),
            sa.Column("resolved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index("ix_reservation_status_disputes_id", "reservation_status_disputes", ["id"])
        op.create_index("ix_reservation_status_disputes_reservation_id", "reservation_status_disputes", ["reservation_id"])
        op.create_index("ix_reservation_status_disputes_guest_id", "reservation_status_disputes", ["guest_id"])
        op.create_index("ix_reservation_status_disputes_status", "reservation_status_disputes", ["status"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if inspector.has_table("reservation_status_disputes"):
        for index_name in ("ix_reservation_status_disputes_status", "ix_reservation_status_disputes_guest_id", "ix_reservation_status_disputes_reservation_id", "ix_reservation_status_disputes_id"):
            if index_name in {x["name"] for x in inspect(bind).get_indexes("reservation_status_disputes")}:
                op.drop_index(index_name, table_name="reservation_status_disputes")
        op.drop_table("reservation_status_disputes")
    sa.Enum(name="reservationdisputestatus").drop(bind, checkfirst=True)
    if inspector.has_table("notifications"):
        indexes = {x["name"] for x in inspect(bind).get_indexes("notifications")}
        for index_name in ("ix_notifications_hotel_id", "ix_notifications_user_id"):
            if index_name in indexes:
                op.drop_index(index_name, table_name="notifications")
        op.drop_table("notifications")
