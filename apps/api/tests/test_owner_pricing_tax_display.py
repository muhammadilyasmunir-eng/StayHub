from pathlib import Path


OWNER_PRICING = Path(__file__).parents[1] / "app" / "static" / "owner-pricing.js"


def test_owner_room_type_pricing_prefers_fresh_property_tax_configuration():
    source = OWNER_PRICING.read_text(encoding="utf-8")
    assert "const selectedHotel" in source
    assert "selectedHotel?.tax_percent" in source
    assert "const tax = Number(window.__stayhubTax ?? selectedHotel?.tax_percent ?? 0)" in source


def test_owner_pricing_tax_fallback_still_supports_selected_property():
    source = OWNER_PRICING.read_text(encoding="utf-8")
    assert "const configured=selectedHotel?.tax_percent ?? window.__stayhubTax" in source
