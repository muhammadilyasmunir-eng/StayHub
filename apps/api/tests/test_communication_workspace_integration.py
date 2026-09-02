from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"


def test_owner_portal_message_workspace_is_loaded():
    html = (STATIC / "owner-portal-pro.html").read_text(encoding="utf-8")
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    js = (STATIC / "owner-notification-center.js").read_text(encoding="utf-8")
    assert 'id="messages"' in html
    assert "owner-notification-center.js" in main
    assert "window.data?.res" not in js
    assert "/reservations/hotel/" in js


def test_owner_notifications_are_clickable_and_persist_in_messages_history():
    js = (STATIC / "owner-notification-center.js").read_text(encoding="utf-8")
    assert "data-notification-id" in js
    assert "openNotification" in js
    assert "systemNotifications" in js
    assert "System notification" in js
    assert "for(const n of fresh)fetch" not in js


def test_admin_portal_message_workspace_uses_admin_session():
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    js = (STATIC / "admin-reservation-disputes.js").read_text(encoding="utf-8")
    assert "admin-reservation-disputes.js" in main
    assert "stayhub_admin_token" in js
    assert "sender_role==='admin'" in js


def test_customer_messaging_and_guest_request_contracts():
    detail = (STATIC / "reservation-messages.js").read_text(encoding="utf-8")
    reservation = (ROOT / "app" / "api" / "reservation.py").read_text(encoding="utf-8")
    assert "Guest Request" in detail
    assert '"owner_user_id"' in reservation
    assert (STATIC / "customer-messages.html").exists()
    assert (STATIC / "customer-messages.js").exists()


def test_public_property_facilities_contract():
    html = (STATIC / "public" / "hotel.html").read_text(encoding="utf-8")
    js = (STATIC / "public" / "public-hotel-facilities.js").read_text(encoding="utf-8")
    assert "public-hotel-facilities.js" in html
    assert "Most Popular Facilities" in js
    assert "hotel.facilities" in js
