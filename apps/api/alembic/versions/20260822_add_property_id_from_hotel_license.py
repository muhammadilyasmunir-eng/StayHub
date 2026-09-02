"""add unique licence-backed property IDs

Revision ID: 20260822_property_id
Revises: 8c3f2d1a7b90
"""

from alembic import op
import sqlalchemy as sa

revision = "20260822_property_id"
down_revision = "8c3f2d1a7b90"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("hotels")}

    if "property_id" not in columns:
        op.add_column("hotels", sa.Column("property_id", sa.String(length=50), nullable=True))

    # Use the submitted hotel licence when it is a valid 6+ digit value.
    # Legacy rows without a valid licence receive a unique 6-digit temporary
    # identity derived from the existing immutable hotel ID; an admin can replace
    # that value with the real licence from the new Property Edit screen.
    op.execute(
        """
        UPDATE hotels h
        SET property_id = COALESCE(
            (
                SELECT d.license_number
                FROM hotel_documents d
                WHERE d.hotel_id = h.id
                  AND d.license_number ~ '^[0-9]{6,}$'
                ORDER BY d.id
                LIMIT 1
            ),
            (600000 + h.id)::text
        )
        WHERE h.property_id IS NULL
        """
    )

    op.alter_column(
        "hotels",
        "property_id",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    existing_constraints = {c["name"] for c in inspector.get_unique_constraints("hotels")}
    if "uq_hotels_property_id" not in existing_constraints:
        op.create_unique_constraint("uq_hotels_property_id", "hotels", ["property_id"])

    existing_indexes = {i["name"] for i in inspector.get_indexes("hotels")}
    if "ix_hotels_property_id" not in existing_indexes:
        op.create_index("ix_hotels_property_id", "hotels", ["property_id"], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {i["name"] for i in inspector.get_indexes("hotels")}
    if "ix_hotels_property_id" in existing_indexes:
        op.drop_index("ix_hotels_property_id", table_name="hotels")

    existing_constraints = {c["name"] for c in inspector.get_unique_constraints("hotels")}
    if "uq_hotels_property_id" in existing_constraints:
        op.drop_constraint("uq_hotels_property_id", "hotels", type_="unique")

    columns = {c["name"] for c in inspector.get_columns("hotels")}
    if "property_id" in columns:
        op.drop_column("hotels", "property_id")
