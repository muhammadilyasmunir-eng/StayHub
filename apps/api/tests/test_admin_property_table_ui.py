from pathlib import Path


def test_admin_property_table_shows_identity_registration_date_and_working_view_action():
    html_path = Path(__file__).resolve().parents[1] / "app" / "static" / "admin-panel.html"
    source = html_path.read_text(encoding="utf-8")

    assert "<th>S.No</th>" in source
    assert "Property ID / Licence" in source
    assert "<th>Owner ID</th>" in source
    assert "<th>Property Name</th>" in source
    assert "<th>Registration Date</th>" in source
    assert "formatDate(h.created_at)" in source
    assert "onclick=\"inspect(${h.id})\"" in source
    assert "function formatDate(v)" in source
    assert "h.owner_id" in source
    assert "h.property_id" in source


def test_hotel_list_response_exposes_admin_table_identity_fields():
    schema_path = Path(__file__).resolve().parents[1] / "app" / "schemas" / "hotel.py"
    source = schema_path.read_text(encoding="utf-8")

    assert "property_id: str" in source
    assert "owner_id: int | None = None" in source
    assert "created_at: object | None = None" in source
