"""complete owner registration fields

Revision ID: 7d2a1f9c4e61
Revises: 521806218c06
"""

from alembic import op
import sqlalchemy as sa


revision = "7d2a1f9c4e61"
down_revision = "521806218c06"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(length=100), nullable=True))
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.add_column("hotel_documents", sa.Column("license_number", sa.String(length=255), nullable=True))
    op.add_column("hotel_documents", sa.Column("registration_number", sa.String(length=255), nullable=True))

    op.add_column("hotel_policies", sa.Column("house_rules", sa.Text(), nullable=True))

    op.add_column("room_types", sa.Column("extra_bed_available", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("room_types", sa.Column("extra_bed_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("room_types", sa.Column("extra_bed_information", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("room_types", "extra_bed_information")
    op.drop_column("room_types", "extra_bed_price")
    op.drop_column("room_types", "extra_bed_available")
    op.drop_column("hotel_policies", "house_rules")
    op.drop_column("hotel_documents", "registration_number")
    op.drop_column("hotel_documents", "license_number")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
    op.drop_column("users", "phone")
