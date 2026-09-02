from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_public_hotel_reads_owner_calendar():
    source = read("app/api/public_hotels.py")
    assert "RoomAvailability" in source
    assert "check_in: date | None" in source
    assert "check_out: date | None" in source
    assert "rooms_to_sell" in source
    assert "net_booked" in source
    assert "bookable" in source


def test_owner_calendar_is_based_on_reservations():
    source = read("app/api/availability.py")
    assert "booked_by_day" in source
    assert "ReservationStatus.CANCELLED" in source
    assert "ReservationStatus.NO_SHOW" in source
    assert '"net_booked"' in source
    assert '"available"' in source


def test_owner_and_admin_reservation_payloads_expose_payment_and_guest_details():
    owner_source = read("app/api/reservation.py")
    admin_source = read("app/api/admin/reservations.py")
    for source in (owner_source, admin_source):
        assert "payment_method" in source
        assert "payment_status" in source
        assert "confirmation_no" in source
        assert "guest_name" in source
        assert "room_type_name" in source
        assert "total_amount" in source


def test_admin_reservations_ui_exists():
    source = read("app/static/admin-live-properties-ui.js")
    assert "stayhubAdminReservations" in source
    assert "/admin/reservations/" in source


def test_public_hotel_refreshes_after_date_search():
    source = read("app/static/public/hotel.js")
    assert "async function loadHotel" in source
    assert "check_in" in source
    assert "check_out" in source
    assert "await loadHotel()" in source
