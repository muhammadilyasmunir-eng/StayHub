from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"


def test_owner_portal_message_workspace_is_loaded():
    html = (STATIC / "owner-portal-pro.html").read_text(encoding="utf-8")
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert 'id="messages"' in html
    assert "owner-notification-center.js" in main


def test_admin_portal_message_workspace_is_loaded():
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "admin-reservation-disputes.js" in main


def test_admin_messages_use_admin_session():
    js = (STATIC / "admin-reservation-disputes.js").read_text(encoding="utf-8")
    assert "stayhub_admin_token" in js
    assert "sender_role==='admin'" in js


def test_owner_messages_load_selected_hotel_reservations():
    js = (STATIC / "owner-notification-center.js").read_text(encoding="utf-8")
    assert "window.data?.res" not in js
    assert "/reservations/hotel/" in js


def test_customer_detail_exposes_owner_and_guest_request_ui():
    js = (STATIC / "reservation-messages.js").read_text(encoding="utf-8")
    reservation = (ROOT / "app" / "api" / "reservation.py").read_text(encoding="utf-8")
    assert "Guest Request" in js
    assert "recipient_user_id" in js
    assert '"owner_user_id"' in reservation


def test_customer_messages_page_exists():
    assert (STATIC / "customer-messages.html").exists()
    assert (STATIC / "customer-messages.js").exists()
