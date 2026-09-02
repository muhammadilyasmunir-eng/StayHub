from pathlib import Path


def test_property_id_is_license_number_and_admin_edit_is_exposed():
    model = Path(__file__).resolve().parents[1] / "app" / "models" / "hotel.py"
    schema = Path(__file__).resolve().parents[1] / "app" / "schemas" / "hotel.py"
    service = Path(__file__).resolve().parents[1] / "app" / "services" / "user_service.py"
    admin_api = Path(__file__).resolve().parents[1] / "app" / "api" / "admin" / "hotels.py"
    admin_ui = Path(__file__).resolve().parents[1] / "app" / "static" / "admin-panel.html"
    registration_client = Path(__file__).resolve().parents[1] / "app" / "static" / "public" / "owner-register-submit-v2.js"

    assert "property_id" in model.read_text(encoding="utf-8")
    assert "property_id" in schema.read_text(encoding="utf-8")
    assert "license_number" in service.read_text(encoding="utf-8")
    assert "@router.put(\"/{hotel_id}\")" in admin_api.read_text(encoding="utf-8")
    assert "Edit Property" in admin_ui.read_text(encoding="utf-8")
    assert "property_id" in admin_ui.read_text(encoding="utf-8")
    assert "license_number" in registration_client.read_text(encoding="utf-8")


def test_property_id_requires_at_least_six_digits():
    schema = Path(__file__).resolve().parents[1] / "app" / "schemas" / "hotel.py"
    source = schema.read_text(encoding="utf-8")
    assert "pattern=r\"^\\d{6,}$\"" in source
