"""add complete room registration

Revision ID: c4ab07302039
Revises: f4253188aac8
Create Date: 2026-08-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4ab07302039"
down_revision: Union[str, Sequence[str], None] = "f4253188aac8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # Existing room_types columns
    # Add only if missing
    # ---------------------------------------------------------

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    room_type_columns = {
        column["name"]
        for column in inspector.get_columns("room_types")
    }

    if "number_of_rooms" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "number_of_rooms",
                sa.Integer(),
                nullable=False,
                server_default="1",
            ),
        )

    if "bed_type" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "bed_type",
                sa.String(length=100),
                nullable=True,
            ),
        )

    if "room_size" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "room_size",
                sa.String(length=100),
                nullable=True,
            ),
        )

    if "smoking_allowed" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "smoking_allowed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )

    # ---------------------------------------------------------
    # Room Type Facilities
    # ---------------------------------------------------------

    existing_tables = set(inspector.get_table_names())

    if "room_type_facilities" not in existing_tables:

        op.create_table(
            "room_type_facilities",

            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                nullable=False,
            ),

            sa.Column(
                "room_type_id",
                sa.Integer(),
                nullable=False,
            ),

            sa.Column(
                "name",
                sa.String(length=150),
                nullable=False,
            ),

            sa.Column(
                "available",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),

            sa.ForeignKeyConstraint(
                ["room_type_id"],
                ["room_types.id"],
                ondelete="CASCADE",
            ),
        )

        op.create_index(
            "ix_room_type_facilities_id",
            "room_type_facilities",
            ["id"],
            unique=False,
        )

        op.create_index(
            "ix_room_type_facilities_room_type_id",
            "room_type_facilities",
            ["room_type_id"],
            unique=False,
        )

    # ---------------------------------------------------------
    # Room Type Photos
    # ---------------------------------------------------------

    if "room_type_photos" not in existing_tables:

        op.create_table(
            "room_type_photos",

            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                nullable=False,
            ),

            sa.Column(
                "room_type_id",
                sa.Integer(),
                nullable=False,
            ),

            sa.Column(
                "photo_url",
                sa.String(length=1000),
                nullable=False,
            ),

            sa.Column(
                "caption",
                sa.String(length=255),
                nullable=True,
            ),

            sa.Column(
                "is_primary",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),

            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),

            sa.ForeignKeyConstraint(
                ["room_type_id"],
                ["room_types.id"],
                ondelete="CASCADE",
            ),
        )

        op.create_index(
            "ix_room_type_photos_id",
            "room_type_photos",
            ["id"],
            unique=False,
        )

        op.create_index(
            "ix_room_type_photos_room_type_id",
            "room_type_photos",
            ["room_type_id"],
            unique=False,
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())

    # ---------------------------------------------------------
    # Remove Room Type Photos
    # ---------------------------------------------------------

    if "room_type_photos" in existing_tables:

        existing_indexes = {
            index["name"]
            for index in inspector.get_indexes(
                "room_type_photos"
            )
        }

        if "ix_room_type_photos_room_type_id" in existing_indexes:
            op.drop_index(
                "ix_room_type_photos_room_type_id",
                table_name="room_type_photos",
            )

        if "ix_room_type_photos_id" in existing_indexes:
            op.drop_index(
                "ix_room_type_photos_id",
                table_name="room_type_photos",
            )

        op.drop_table("room_type_photos")

    # ---------------------------------------------------------
    # Remove Room Type Facilities
    # ---------------------------------------------------------

    if "room_type_facilities" in existing_tables:

        existing_indexes = {
            index["name"]
            for index in inspector.get_indexes(
                "room_type_facilities"
            )
        }

        if "ix_room_type_facilities_room_type_id" in existing_indexes:
            op.drop_index(
                "ix_room_type_facilities_room_type_id",
                table_name="room_type_facilities",
            )

        if "ix_room_type_facilities_id" in existing_indexes:
            op.drop_index(
                "ix_room_type_facilities_id",
                table_name="room_type_facilities",
            )

        op.drop_table("room_type_facilities")

    # ---------------------------------------------------------
    # Remove room_types columns
    # ---------------------------------------------------------

    room_type_columns = {
        column["name"]
        for column in inspector.get_columns("room_types")
    }

    if "smoking_allowed" in room_type_columns:
        op.drop_column(
            "room_types",
            "smoking_allowed",
        )

    if "room_size" in room_type_columns:
        op.drop_column(
            "room_types",
            "room_size",
        )

    if "bed_type" in room_type_columns:
        op.drop_column(
            "room_types",
            "bed_type",
        )

    if "number_of_rooms" in room_type_columns:
        op.drop_column(
            "room_types",
            "number_of_rooms",
        )
