from datetime import date
from decimal import Decimal

from app.services.reservation_pricing import build_daily_rate_breakdown


def test_daily_rate_breakdown_uses_each_calendar_rate():
    rows = {
        date(2026, 8, 29): {"rate": Decimal("10000"), "bookable": True},
        date(2026, 8, 30): {"rate": Decimal("15000"), "bookable": True},
    }

    result = build_daily_rate_breakdown(
        date(2026, 8, 29),
        date(2026, 8, 31),
        rows,
        Decimal("0"),
        Decimal("0"),
    )

    assert [item["base_price"] for item in result] == [Decimal("10000.00"), Decimal("15000.00")]
    assert sum(item["selling_price"] for item in result) == Decimal("25000.00")
    assert sum(item["total_price"] for item in result) == Decimal("25000.00")
