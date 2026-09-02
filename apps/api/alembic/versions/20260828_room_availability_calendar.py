"""add daily room availability calendar

Revision ID: 20260828_room_availability_calendar
Revises: 20260828_reservation_payment_methods
"""
from alembic import op

revision = "20260828_room_availability_calendar"
down_revision = "20260828_reservation_payment_methods"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The application also uses Base.metadata.create_all() at startup.  Keep
    # this migration idempotent so a startup-created table can be adopted by
    # Alembic without failing the upgrade.
    op.execute("""
        CREATE TABLE IF NOT EXISTS room_availability (
            id SERIAL PRIMARY KEY,
            room_type_id INTEGER NOT NULL REFERENCES room_types(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            rooms_to_sell INTEGER NOT NULL DEFAULT 0,
            rate NUMERIC(10, 2) NOT NULL DEFAULT 0,
            bookable BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_room_availability_type_date UNIQUE (room_type_id, date)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_room_availability_room_type_id ON room_availability(room_type_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_room_availability_date ON room_availability(date)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS room_availability")
