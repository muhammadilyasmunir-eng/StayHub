from decimal import Decimal

from app.services.pricing import calculate_room_price


def test_room_price_applies_discount_then_tax():
    result = calculate_room_price(
        Decimal("123.00"),
        Decimal("10"),
        Decimal("16"),
    )

    assert result.base_price == Decimal("123.00")
    assert result.discount_amount == Decimal("12.30")
    assert result.selling_price == Decimal("110.70")
    assert result.tax_amount == Decimal("17.71")
    assert result.total_price == Decimal("128.41")


def test_zero_discount_and_tax_keep_base_price():
    result = calculate_room_price(
        Decimal("100.00"),
        Decimal("0"),
        Decimal("0"),
    )

    assert result.selling_price == Decimal("100.00")
    assert result.tax_amount == Decimal("0.00")
    assert result.total_price == Decimal("100.00")
