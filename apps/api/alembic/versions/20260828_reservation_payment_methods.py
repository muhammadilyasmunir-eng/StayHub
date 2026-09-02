"""add payment method fields to reservations

Revision ID: 20260828_reservation_payment_methods
Revises: 20260828_add_awaiting_terms_status
"""
from alembic import op
import sqlalchemy as sa

revision = "20260828_reservation_payment_methods"
down_revision = "20260828_add_awaiting_terms_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reservations", sa.Column("payment_method", sa.String(length=30), nullable=True))
    op.add_column("reservations", sa.Column("payment_status", sa.String(length=30), nullable=True))
    op.add_column("reservations", sa.Column("payment_reference", sa.String(length=100), nullable=True))
    op.add_column("reservations", sa.Column("card_last4", sa.String(length=4), nullable=True))
    op.execute("UPDATE reservations SET payment_method='pay_at_property' WHERE payment_method IS NULL")
    op.execute("UPDATE reservations SET payment_status='pending' WHERE payment_status IS NULL")
    op.alter_column("reservations", "payment_method", nullable=False)
    op.alter_column("reservations", "payment_status", nullable=False)


def downgrade() -> None:
    op.drop_column("reservations", "card_last4")
    op.drop_column("reservations", "payment_reference")
    op.drop_column("reservations", "payment_status")
    op.drop_column("reservations", "payment_method")
