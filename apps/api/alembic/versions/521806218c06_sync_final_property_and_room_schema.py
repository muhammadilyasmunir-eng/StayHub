"""sync final property and room schema

Revision ID: 521806218c06
Revises: c4ab07302039
Create Date: 2026-08-11 12:36:14.248087

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "521806218c06"
down_revision: Union[str, Sequence[str], None] = "c4ab07302039"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ============================================================
    # 1. HOTEL DOCUMENTS
    # ============================================================

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotel_documents")
    }

    if "ix_hotel_documents_id" not in existing_indexes:
        op.create_index(
            "ix_hotel_documents_id",
            "hotel_documents",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 2. HOTEL FACILITIES
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_facility_columns = {
        column["name"]
        for column in inspector.get_columns("hotel_facilities")
    }

    if "created_at" not in hotel_facility_columns:
        op.add_column(
            "hotel_facilities",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotel_facilities")
    }

    if "ix_hotel_facilities_id" not in existing_indexes:
        op.create_index(
            "ix_hotel_facilities_id",
            "hotel_facilities",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 3. HOTEL PHOTOS
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotel_photos")
    }

    if "ix_hotel_photos_id" not in existing_indexes:
        op.create_index(
            "ix_hotel_photos_id",
            "hotel_photos",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 4. HOTEL POLICIES
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotel_policies")
    }

    if "ix_hotel_policies_id" not in existing_indexes:
        op.create_index(
            "ix_hotel_policies_id",
            "hotel_policies",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 5. HOTELS - ADDITIONAL COLUMNS
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]
        for column in inspector.get_columns("hotels")
    }

    if "description" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "description",
                sa.Text(),
                nullable=True,
            ),
        )

    if "alternate_phone" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "alternate_phone",
                sa.String(length=50),
                nullable=True,
            ),
        )

    if "postal_code" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "postal_code",
                sa.String(length=30),
                nullable=True,
            ),
        )

    if "latitude" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "latitude",
                sa.Float(),
                nullable=True,
            ),
        )

    if "longitude" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "longitude",
                sa.Float(),
                nullable=True,
            ),
        )

    if "rejection_reason" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "rejection_reason",
                sa.String(length=1000),
                nullable=True,
            ),
        )

    if "approved_at" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "approved_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if "approved_by" not in hotel_columns:
        op.add_column(
            "hotels",
            sa.Column(
                "approved_by",
                sa.Integer(),
                nullable=True,
            ),
        )

    # ============================================================
    # 6. HOTELS - EXISTING NULL DATA
    #
    # Existing hotels must receive safe values before NOT NULL.
    # ============================================================

    op.execute(
        """
        UPDATE hotels
        SET property_type = 'Hotel'
        WHERE property_type IS NULL
        """
    )

    op.execute(
        """
        UPDATE hotels
        SET total_rooms = 1
        WHERE total_rooms IS NULL
        """
    )

    op.execute(
        """
        UPDATE hotels
        SET check_in_time = '14:00'
        WHERE check_in_time IS NULL
        """
    )

    op.execute(
        """
        UPDATE hotels
        SET check_out_time = '12:00'
        WHERE check_out_time IS NULL
        """
    )

    # ============================================================
    # 7. HOTEL PROPERTY TYPE
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    if hotel_columns["property_type"]["nullable"]:
        op.alter_column(
            "hotels",
            "property_type",
            existing_type=sa.String(length=100),
            nullable=False,
        )

    # ============================================================
    # 8. HOTEL STAR RATING
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    current_star_type = hotel_columns["star_rating"]["type"]

    if not isinstance(current_star_type, sa.Float):
        op.alter_column(
            "hotels",
            "star_rating",
            existing_type=sa.NUMERIC(
                precision=2,
                scale=1,
            ),
            type_=sa.Float(),
            existing_nullable=True,
        )

    # ============================================================
    # 9. HOTEL TOTAL ROOMS
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    if hotel_columns["total_rooms"]["nullable"]:
        op.alter_column(
            "hotels",
            "total_rooms",
            existing_type=sa.Integer(),
            nullable=False,
        )

    # ============================================================
    # 10. HOTEL CHECK-IN TIME
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    op.alter_column(
        "hotels",
        "check_in_time",
        existing_type=sa.String(length=20),
        type_=sa.String(length=10),
        existing_nullable=hotel_columns["check_in_time"]["nullable"],
        nullable=False,
    )

    # ============================================================
    # 11. HOTEL CHECK-OUT TIME
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    op.alter_column(
        "hotels",
        "check_out_time",
        existing_type=sa.String(length=20),
        type_=sa.String(length=10),
        existing_nullable=hotel_columns["check_out_time"]["nullable"],
        nullable=False,
    )

    # ============================================================
    # 12. HOTEL STATUS ENUM
    # ============================================================

    hotel_status_enum = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SUSPENDED",
        "INACTIVE",
        name="hotelstatus",
    )

    hotel_status_enum.create(
        bind,
        checkfirst=True,
    )

    # Existing boolean status must be converted safely.
    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    status_type = str(
        hotel_columns["status"]["type"]
    ).lower()

    if "boolean" in status_type:
        op.execute(
            """
            ALTER TABLE hotels
            ALTER COLUMN status DROP DEFAULT
            """
        )

        op.alter_column(
            "hotels",
            "status",
            type_=hotel_status_enum,
            postgresql_using="""
                CASE
                    WHEN status = TRUE
                    THEN 'APPROVED'::hotelstatus
                    ELSE 'PENDING'::hotelstatus
                END
            """,
            existing_nullable=False,
        )

    # ============================================================
    # 13. HOTEL STATUS INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotels")
    }

    if "ix_hotels_status" not in existing_indexes:
        op.create_index(
            "ix_hotels_status",
            "hotels",
            ["status"],
            unique=False,
        )

    # ============================================================
    # 14. APPROVED_BY FOREIGN KEY
    # ============================================================

    inspector = sa.inspect(bind)

    foreign_keys = inspector.get_foreign_keys("hotels")

    approved_by_fk_exists = any(
        fk.get("constrained_columns") == ["approved_by"]
        and fk.get("referred_table") == "users"
        and fk.get("referred_columns") == ["id"]
        for fk in foreign_keys
    )

    if not approved_by_fk_exists:
        op.create_foreign_key(
            "fk_hotels_approved_by_users",
            "hotels",
            "users",
            ["approved_by"],
            ["id"],
            ondelete="SET NULL",
        )

    # ============================================================
    # 15. ROOM TYPE FACILITIES - ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_type_facilities"
        )
    }

    if "ix_room_type_facilities_id" not in existing_indexes:
        op.create_index(
            "ix_room_type_facilities_id",
            "room_type_facilities",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 16. ROOM TYPE PHOTOS - ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_type_photos"
        )
    }

    if "ix_room_type_photos_id" not in existing_indexes:
        op.create_index(
            "ix_room_type_photos_id",
            "room_type_photos",
            ["id"],
            unique=False,
        )

    # ============================================================
    # 17. ROOM TYPES - ROOM SIZE
    # ============================================================

    inspector = sa.inspect(bind)

    room_type_columns = {
        column["name"]: column
        for column in inspector.get_columns("room_types")
    }

    current_room_size_type = str(
        room_type_columns["room_size"]["type"]
    ).lower()

    if "numeric" in current_room_size_type:
        op.alter_column(
            "room_types",
            "room_size",
            existing_type=sa.NUMERIC(
                precision=8,
                scale=2,
            ),
            type_=sa.String(length=100),
            existing_nullable=True,
        )

    # ============================================================
    # 18. ROOM TYPES - HOTEL ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_types"
        )
    }

    if "ix_room_types_hotel_id" not in existing_indexes:
        op.create_index(
            "ix_room_types_hotel_id",
            "room_types",
            ["hotel_id"],
            unique=False,
        )

    # ============================================================
    # 19. ROOM TYPES - REMOVE OLD COLUMNS
    # ============================================================

    inspector = sa.inspect(bind)

    room_type_columns = {
        column["name"]
        for column in inspector.get_columns("room_types")
    }

    if "total_rooms" in room_type_columns:
        op.drop_column(
            "room_types",
            "total_rooms",
        )

    if "room_size_unit" in room_type_columns:
        op.drop_column(
            "room_types",
            "room_size_unit",
        )


def downgrade() -> None:
    """Downgrade schema."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ============================================================
    # 1. RESTORE ROOM TYPE COLUMNS
    # ============================================================

    room_type_columns = {
        column["name"]
        for column in inspector.get_columns("room_types")
    }

    if "room_size_unit" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "room_size_unit",
                sa.String(length=20),
                server_default=sa.text("'sqm'"),
                nullable=True,
            ),
        )

    if "total_rooms" not in room_type_columns:
        op.add_column(
            "room_types",
            sa.Column(
                "total_rooms",
                sa.Integer(),
                server_default=sa.text("1"),
                nullable=True,
            ),
        )

    # ============================================================
    # 2. ROOM TYPE HOTEL ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_types"
        )
    }

    if "ix_room_types_hotel_id" in existing_indexes:
        op.drop_index(
            "ix_room_types_hotel_id",
            table_name="room_types",
        )

    # ============================================================
    # 3. ROOM SIZE BACK TO NUMERIC
    # ============================================================

    inspector = sa.inspect(bind)

    room_type_columns = {
        column["name"]: column
        for column in inspector.get_columns("room_types")
    }

    current_room_size_type = str(
        room_type_columns["room_size"]["type"]
    ).lower()

    if "character" in current_room_size_type:
        op.alter_column(
            "room_types",
            "room_size",
            existing_type=sa.String(length=100),
            type_=sa.NUMERIC(
                precision=8,
                scale=2,
            ),
            existing_nullable=True,
            postgresql_using="""
                NULLIF(
                    regexp_replace(room_size, '[^0-9.]', '', 'g'),
                    ''
                )::numeric
            """,
        )

    # ============================================================
    # 4. ROOM TYPE PHOTOS ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_type_photos"
        )
    }

    if "ix_room_type_photos_id" in existing_indexes:
        op.drop_index(
            "ix_room_type_photos_id",
            table_name="room_type_photos",
        )

    # ============================================================
    # 5. ROOM TYPE FACILITIES ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "room_type_facilities"
        )
    }

    if "ix_room_type_facilities_id" in existing_indexes:
        op.drop_index(
            "ix_room_type_facilities_id",
            table_name="room_type_facilities",
        )

    # ============================================================
    # 6. REMOVE APPROVED_BY FOREIGN KEY
    # ============================================================

    inspector = sa.inspect(bind)

    foreign_keys = inspector.get_foreign_keys("hotels")

    for fk in foreign_keys:
        constrained_columns = fk.get(
            "constrained_columns"
        ) or []

        if constrained_columns == ["approved_by"]:
            constraint_name = fk.get("name")

            if constraint_name:
                op.drop_constraint(
                    constraint_name,
                    "hotels",
                    type_="foreignkey",
                )

    # ============================================================
    # 7. HOTEL STATUS INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("hotels")
    }

    if "ix_hotels_status" in existing_indexes:
        op.drop_index(
            "ix_hotels_status",
            table_name="hotels",
        )

    # ============================================================
    # 8. HOTEL STATUS BACK TO BOOLEAN
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]: column
        for column in inspector.get_columns("hotels")
    }

    status_type = str(
        hotel_columns["status"]["type"]
    ).lower()

    if "user-defined" in status_type or "hotelstatus" in status_type:
        op.alter_column(
            "hotels",
            "status",
            existing_type=sa.Enum(
                "PENDING",
                "APPROVED",
                "REJECTED",
                "SUSPENDED",
                "INACTIVE",
                name="hotelstatus",
            ),
            type_=sa.Boolean(),
            existing_nullable=False,
            postgresql_using="""
                CASE
                    WHEN status = 'APPROVED'
                    THEN TRUE
                    ELSE FALSE
                END
            """,
        )

    # ============================================================
    # 9. HOTEL CHECK-OUT TIME
    # ============================================================

    op.alter_column(
        "hotels",
        "check_out_time",
        existing_type=sa.String(length=10),
        type_=sa.String(length=20),
        existing_nullable=False,
        nullable=True,
    )

    # ============================================================
    # 10. HOTEL CHECK-IN TIME
    # ============================================================

    op.alter_column(
        "hotels",
        "check_in_time",
        existing_type=sa.String(length=10),
        type_=sa.String(length=20),
        existing_nullable=False,
        nullable=True,
    )

    # ============================================================
    # 11. HOTEL TOTAL ROOMS
    # ============================================================

    op.alter_column(
        "hotels",
        "total_rooms",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # ============================================================
    # 12. HOTEL STAR RATING
    # ============================================================

    op.alter_column(
        "hotels",
        "star_rating",
        existing_type=sa.Float(),
        type_=sa.NUMERIC(
            precision=2,
            scale=1,
        ),
        existing_nullable=True,
    )

    # ============================================================
    # 13. HOTEL PROPERTY TYPE
    # ============================================================

    op.alter_column(
        "hotels",
        "property_type",
        existing_type=sa.String(length=100),
        nullable=True,
    )

    # ============================================================
    # 14. REMOVE HOTEL COLUMNS
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_columns = {
        column["name"]
        for column in inspector.get_columns("hotels")
    }

    if "approved_by" in hotel_columns:
        op.drop_column(
            "hotels",
            "approved_by",
        )

    if "approved_at" in hotel_columns:
        op.drop_column(
            "hotels",
            "approved_at",
        )

    if "rejection_reason" in hotel_columns:
        op.drop_column(
            "hotels",
            "rejection_reason",
        )

    if "longitude" in hotel_columns:
        op.drop_column(
            "hotels",
            "longitude",
        )

    if "latitude" in hotel_columns:
        op.drop_column(
            "hotels",
            "latitude",
        )

    if "postal_code" in hotel_columns:
        op.drop_column(
            "hotels",
            "postal_code",
        )

    if "alternate_phone" in hotel_columns:
        op.drop_column(
            "hotels",
            "alternate_phone",
        )

    if "description" in hotel_columns:
        op.drop_column(
            "hotels",
            "description",
        )

    # ============================================================
    # 15. HOTEL POLICIES ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "hotel_policies"
        )
    }

    if "ix_hotel_policies_id" in existing_indexes:
        op.drop_index(
            "ix_hotel_policies_id",
            table_name="hotel_policies",
        )

    # ============================================================
    # 16. HOTEL PHOTOS ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "hotel_photos"
        )
    }

    if "ix_hotel_photos_id" in existing_indexes:
        op.drop_index(
            "ix_hotel_photos_id",
            table_name="hotel_photos",
        )

    # ============================================================
    # 17. HOTEL FACILITIES ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "hotel_facilities"
        )
    }

    if "ix_hotel_facilities_id" in existing_indexes:
        op.drop_index(
            "ix_hotel_facilities_id",
            table_name="hotel_facilities",
        )

    # ============================================================
    # 18. HOTEL FACILITIES CREATED_AT
    # ============================================================

    inspector = sa.inspect(bind)

    hotel_facility_columns = {
        column["name"]
        for column in inspector.get_columns(
            "hotel_facilities"
        )
    }

    if "created_at" in hotel_facility_columns:
        op.drop_column(
            "hotel_facilities",
            "created_at",
        )

    # ============================================================
    # 19. HOTEL DOCUMENTS ID INDEX
    # ============================================================

    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes(
            "hotel_documents"
        )
    }

    if "ix_hotel_documents_id" in existing_indexes:
        op.drop_index(
            "ix_hotel_documents_id",
            table_name="hotel_documents",
        )