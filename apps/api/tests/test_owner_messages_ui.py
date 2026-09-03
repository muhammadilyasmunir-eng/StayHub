from pathlib import Path


def test_owner_customer_messages_ui_uses_compact_conversation_list():
    source = Path("app/static/owner-customer-messages-ui.js").read_text(encoding="utf-8")
    assert "Customer Name + Booking #" in source
    assert "data-conversation-id" in source
    assert "Unread" in source
    assert "markConversationRead" in source


def test_owner_customer_messages_ui_has_right_side_drawer():
    source = Path("app/static/owner-customer-messages-ui.js").read_text(encoding="utf-8")
    assert "ownerMsgDrawer" in source
    assert "position:fixed" in source
    assert "right:0" in source
