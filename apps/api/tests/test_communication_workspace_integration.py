from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"


def test_owner_portal_loads_messages_workspace():
    html = (STATIC / "owner-portal.html").read_text(encoding="utf-8")
    assert "/static/owner-notification-center.js" in html
    assert 'id="messages"' in html


def test_admin_portal_loads_reservations_messages_workspace():
    html = (STATIC / "admin-panel.html").read_text(encoding="utf-8")
    assert "/static/admin-reservation-disputes.js" in html


def test_admin_workspace_uses_admin_token_and_role_not_missing_local_id():
    js = (STATIC / "admin-reservation-disputes.js").read_text(encoding="utf-8")
    assert "stayhub_admin_token" in js
    assert "sender_role==='admin'" in js or "sender_role === 'admin'" in js


def test_owner_messages_do_not_depend_on_window_data_for_reservations():
    js = (STATIC / "owner-notification-center.js").read_text(encoding="utf-8")
    assert "window.data?.res" not in js
    assert "/reservations/hotel/" in js


def test_customer_reservation_detail_exposes_owner_and_guest_request():
    js = (STATIC / "reservation-messages.js").read_text(encoding="utf-8")
    assert "Guest Request" in js
    assert "recipient_user_id" in js
