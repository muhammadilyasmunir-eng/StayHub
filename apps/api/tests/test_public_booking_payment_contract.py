from pathlib import Path


def test_public_booking_payment_contract_is_present():
    root = Path(__file__).resolve().parents[1]
    schema = (root / "app" / "schemas" / "public_booking.py").read_text(encoding="utf-8")
    api = (root / "app" / "api" / "public_bookings.py").read_text(encoding="utf-8")
    config = (root / "app" / "core" / "config.py").read_text(encoding="utf-8")
    model = (root / "app" / "models" / "reservation.py").read_text(encoding="utf-8")
    booking = (root / "app" / "static" / "public" / "booking.js").read_text(encoding="utf-8")

    for value in ("pay_at_property", "card", "usdt"):
        assert value in schema
        assert value in api
        assert value in booking

    assert "payment_method" in model
    assert "payment_status" in model
    assert "city" in schema
    assert 'name="city"' in booking
    assert "usdt_wallet_address" in config
    assert "USDT_WALLET_ADDRESS" in booking or "payment-options" in booking
    assert "card_number" in booking
    assert "card_cvv" in booking
    assert "card_last4" in schema
