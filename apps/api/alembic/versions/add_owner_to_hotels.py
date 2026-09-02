"""add owner to hotels

Revision ID: 7c91a4f2b8d3
Revises: 2df34d210279
Create Date: 2026-08-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c91a4f2b8d3"
down_revision: Union[str, Sequence[str], None] = "2df34d210279"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "hotels",
        sa.Column("owner_id", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("hotels", "owner_id")