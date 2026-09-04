from pathlib import Path


def test_room_amenities_page_contract_is_wired_to_room_types_and_facilities():
    root = Path(__file__).resolve().parents[1]
    page = (root / "app" / "static" / "owner-room-amenities.js").read_text(encoding="utf-8")
    api = (root / "app" / "api" / "room_amenities.py").read_text(encoding="utf-8")
    routes = (root / "app" / "api" / "routes.py").read_text(encoding="utf-8")
    main = (root / "app" / "main.py").read_text(encoding="utf-8")
    schema = (root / "app" / "schemas" / "room_type.py").read_text(encoding="utf-8")

    assert "Room Amenities" in page
    assert "All rooms" in page
    assert "Some rooms" in page
    assert "None" in page
    assert "room_sizes" in page
    assert "room_type_ids" in page
    assert "/room-amenities/hotel/" in page
    assert "RoomTypeFacility" in api
    assert "room_types" in api
    assert "room_type_ids" in api
    assert "room_amenities_router" in routes
    assert "owner-room-amenities.js?v=1" in main
    assert "room_size: str | None" in schema


def test_public_room_serializer_exposes_saved_room_amenities():
    root = Path(__file__).resolve().parents[1]
    public_hotels = (root / "app" / "api" / "public_hotels.py").read_text(encoding="utf-8")
    assert '"facilities": [facility.name for facility in room_type.facilities if facility.available]' in public_hotels
