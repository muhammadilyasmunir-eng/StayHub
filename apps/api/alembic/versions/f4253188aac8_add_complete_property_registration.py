from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f4253188aac8"
down_revision = "daf67a25b506"
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # HOTEL - Additional Registration Information
    # ============================================================

    op.add_column(
        "hotels",
        sa.Column(
            "property_type",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "star_rating",
            sa.Numeric(2, 1),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "website",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "total_rooms",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "check_in_time",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "hotels",
        sa.Column(
            "check_out_time",
            sa.String(length=20),
            nullable=True,
        ),
    )

    # ============================================================
    # HOTEL FACILITIES
    # ============================================================

    op.create_table(
        "hotel_facilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "hotel_id",
            sa.Integer(),
            sa.ForeignKey(
                "hotels.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.create_index(
        "ix_hotel_facilities_hotel_id",
        "hotel_facilities",
        ["hotel_id"],
    )

    # ============================================================
    # HOTEL PHOTOS
    # ============================================================

    op.create_table(
        "hotel_photos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "hotel_id",
            sa.Integer(),
            sa.ForeignKey(
                "hotels.id",
                ondelete="CASCADE",
            ),
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
            "category",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    op.create_index(
        "ix_hotel_photos_hotel_id",
        "hotel_photos",
        ["hotel_id"],
    )

    # ============================================================
    # HOTEL POLICIES
    # ============================================================

    op.create_table(
        "hotel_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "hotel_id",
            sa.Integer(),
            sa.ForeignKey(
                "hotels.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "cancellation_policy",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "child_policy",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "pet_policy",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "smoking_policy",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "payment_methods",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "extra_bed_policy",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "age_restriction",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "quiet_hours",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_hotel_policies_hotel_id",
        "hotel_policies",
        ["hotel_id"],
    )

    # ============================================================
    # HOTEL VERIFICATION DOCUMENTS
    # ============================================================

    op.create_table(
        "hotel_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "hotel_id",
            sa.Integer(),
            sa.ForeignKey(
                "hotels.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "document_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "document_number",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "document_url",
            sa.String(length=1000),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "admin_notes",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_hotel_documents_hotel_id",
        "hotel_documents",
        ["hotel_id"],
    )

    # ============================================================
    # ROOM TYPE - Additional Registration Information
    # ============================================================

    op.add_column(
        "room_types",
        sa.Column(
            "bed_type",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "room_types",
        sa.Column(
            "room_size",
            sa.Numeric(8, 2),
            nullable=True,
        ),
    )

    op.add_column(
        "room_types",
        sa.Column(
            "room_size_unit",
            sa.String(length=20),
            nullable=True,
            server_default="sqm",
        ),
    )

    op.add_column(
        "room_types",
        sa.Column(
            "total_rooms",
            sa.Integer(),
            nullable=True,
            server_default="1",
        ),
    )

    # ============================================================
    # ROOM TYPE FACILITIES
    # ============================================================

    op.create_table(
        "room_type_facilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "room_type_id",
            sa.Integer(),
            sa.ForeignKey(
                "room_types.id",
                ondelete="CASCADE",
            ),
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
            server_default=sa.text("true"),
        ),
    )

    op.create_index(
        "ix_room_type_facilities_room_type_id",
        "room_type_facilities",
        ["room_type_id"],
    )

    # ============================================================
    # ROOM TYPE PHOTOS
    # ============================================================

    op.create_table(
        "room_type_photos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "room_type_id",
            sa.Integer(),
            sa.ForeignKey(
                "room_types.id",
                ondelete="CASCADE",
            ),
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
            server_default=sa.text("false"),
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    op.create_index(
        "ix_room_type_photos_room_type_id",
        "room_type_photos",
        ["room_type_id"],
    )


def downgrade():
    # ============================================================
    # ROOM TYPE
    # ============================================================

    op.drop_index(
        "ix_room_type_photos_room_type_id",
        table_name="room_type_photos",
    )

    op.drop_table("room_type_photos")

    op.drop_index(
        "ix_room_type_facilities_room_type_id",
        table_name="room_type_facilities",
    )

    op.drop_table("room_type_facilities")

    op.drop_column(
        "room_types",
        "total_rooms",
    )

    op.drop_column(
        "room_types",
        "room_size_unit",
    )

    op.drop_column(
        "room_types",
        "room_size",
    )

    op.drop_column(
        "room_types",
        "bed_type",
    )

    # ============================================================
    # HOTEL
    # ============================================================

    op.drop_index(
        "ix_hotel_documents_hotel_id",
        table_name="hotel_documents",
    )

    op.drop_table("hotel_documents")

    op.drop_index(
        "ix_hotel_policies_hotel_id",
        table_name="hotel_policies",
    )

    op.drop_table("hotel_policies")

    op.drop_index(
        "ix_hotel_photos_hotel_id",
        table_name="hotel_photos",
    )

    op.drop_table("hotel_photos")

    op.drop_index(
        "ix_hotel_facilities_hotel_id",
        table_name="hotel_facilities",
    )

    op.drop_table("hotel_facilities")

    op.drop_column(
        "hotels",
        "check_out_time",
    )

    op.drop_column(
        "hotels",
        "check_in_time",
    )

    op.drop_column(
        "hotels",
        "total_rooms",
    )

    op.drop_column(
        "hotels",
        "website",
    )

    op.drop_column(
        "hotels",
        "star_rating",
    )

    op.drop_column(
        "hotels",
        "property_type",
    )
