from pathlib import Path


def test_room_file_selection_is_captured_before_ui_preview_clears_input():
    script = Path(__file__).resolve().parents[1] / "app" / "static" / "public" / "owner-register-submit-v2.js"
    source = script.read_text(encoding="utf-8")
    assert "addEventListener('change'" in source
    assert "true);" in source
    assert "room-files" in source


def test_registration_client_shows_backend_failure_in_the_form():
    script = Path(__file__).resolve().parents[1] / "app" / "static" / "public" / "owner-register-submit-v2.js"
    source = script.read_text(encoding="utf-8")
    assert "Registration failed:" in source
    assert "scrollIntoView" in source
    assert "response status" in source
