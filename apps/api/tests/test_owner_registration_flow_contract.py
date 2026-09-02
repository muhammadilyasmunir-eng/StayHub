from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static" / "public"


def test_owner_registration_requires_verified_otp_token():
    users = (ROOT / "app" / "api" / "users.py").read_text(encoding="utf-8-sig")
    assert "X-Owner-OTP-Token" in users
    assert "is_verified" in users
    assert "Owner registration requires a verified email OTP" in users


def test_owner_registration_ui_has_otp_and_property_type_step():
    flow = (STATIC / "owner-register-flow.js").read_text(encoding="utf-8")
    assert "/public/booking-otp/send" in flow
    assert "/public/booking-otp/verify" in flow
    assert "Hotel" in flow and "Apartment" in flow and "Guest House" in flow
    assert "X-Owner-OTP-Token" in flow


def test_demo_seed_is_removed():
    assert not (ROOT / "scripts" / "seed_lahore_demo_hotels.py").exists()
