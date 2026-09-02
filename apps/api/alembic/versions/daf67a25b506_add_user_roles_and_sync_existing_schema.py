"""add user roles and sync existing schema

Revision ID: daf67a25b506
Revises: bcc6387baf5c
Create Date: 2026-08-10 15:55:10.363920
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "daf67a25b506"
down_revision: Union[str, Sequence[str], None] = "bcc6387baf5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Sync existing guests table with current Guest model
    # ---------------------------------------------------------

    op.alter_column(
        "guests",
        "phone",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    op.alter_column(
        "guests",
        "address",
        existing_type=sa.TEXT(),
        type_=sa.String(length=500),
        nullable=False,
    )

    op.alter_column(
        "guests",
        "city",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )

    op.alter_column(
        "guests",
        "country",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )

    op.create_index(
        op.f("ix_guests_hotel_id"),
        "guests",
        ["hotel_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_guests_id_number"),
        "guests",
        ["id_number"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. Create user role enum
    # ---------------------------------------------------------

    user_role_enum = sa.Enum(
        "ADMIN",
        "HOTEL_OWNER",
        "CUSTOMER",
        name="userrole",
    )

    user_role_enum.create(op.get_bind(), checkfirst=True)

    # ---------------------------------------------------------
    # 3. Add role temporarily as nullable
    # ---------------------------------------------------------

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 4. Existing users
    #
    # admin@stayhub.com = StayHub main/admin panel
    # All other existing users remain customers for now.
    #
    # We will NOT assume any existing user is a property owner.
    # ---------------------------------------------------------

    op.execute(
        sa.text(
            """
            UPDATE users
            SET role = 'ADMIN'
            WHERE email = 'admin@stayhub.com'
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET role = 'CUSTOMER'
            WHERE role IS NULL
            """
        )
    )

    # ---------------------------------------------------------
    # 5. Make role required
    # ---------------------------------------------------------

    op.alter_column(
        "users",
        "role",
        existing_type=user_role_enum,
        nullable=False,
    )

    # ---------------------------------------------------------
    # 6. IMPORTANT:
    #
    # Do NOT make hotels.owner_id NOT NULL yet.
    #
    # Existing hotel records are not confirmed to belong to
    # actual property-owner accounts.
    #
    # The property-owner relationship will be assigned when
    # the List Your Property / approval workflow is implemented.
    # ---------------------------------------------------------


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "role",
    )

    sa.Enum(
        "ADMIN",
        "HOTEL_OWNER",
        "CUSTOMER",
        name="userrole",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    op.drop_index(
        op.f("ix_guests_id_number"),
        table_name="guests",
    )

    op.drop_index(
        op.f("ix_guests_hotel_id"),
        table_name="guests",
    )

    op.alter_column(
        "guests",
        "country",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
    )

    op.alter_column(
        "guests",
        "city",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
    )

    op.alter_column(
        "guests",
        "address",
        existing_type=sa.String(length=500),
        type_=sa.TEXT(),
        nullable=True,
    )

    op.alter_column(
        "guests",
        "phone",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )