from pathlib import Path


def test_owner_inventory_wires_room_category_edit_and_persistent_status_controls():
    root = Path(__file__).resolve().parents[1]
    actions = (root / "app" / "static" / "owner-room-category-actions.js").read_text(encoding="utf-8")
    public_hotels = (root / "app" / "api" / "public_hotels.py").read_text(encoding="utf-8")
    main = (root / "app" / "main.py").read_text(encoding="utf-8")

    assert "textContent='Edit'" in actions
    assert "isEnabled=v=>v===true||v===1||v==='1'||v==='true'||v==='True'" in actions
    assert "body:JSON.stringify({status:Boolean(enabled)})" in actions
    assert "applyStatus(id,actual)" in actions
    assert "owner-room-category-actions.js?v=1" in main
    assert "for room_type in hotel.room_types if room_type.status" in public_hotels
