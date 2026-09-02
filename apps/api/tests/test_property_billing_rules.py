from decimal import Decimal
from types import SimpleNamespace

from app.services.commission_service import get_property_commission_percent
from app.services.pricing import property_billing_is_configured


def test_property_billing_requires_both_tax_and_commission_to_be_defined():
    assert property_billing_is_configured(SimpleNamespace(tax_percent=None, commission_percent=None)) is False
    assert property_billing_is_configured(SimpleNamespace(tax_percent=Decimal("16.00"), commission_percent=None)) is False
    assert property_billing_is_configured(SimpleNamespace(tax_percent=None, commission_percent=Decimal("5.00"))) is False
    assert property_billing_is_configured(SimpleNamespace(tax_percent=Decimal("0.00"), commission_percent=Decimal("0.00"))) is True


def test_property_commission_comes_from_property_configuration():
    hotel = SimpleNamespace(commission_percent=Decimal("7.50"))
    assert get_property_commission_percent(hotel) == Decimal("7.50")
