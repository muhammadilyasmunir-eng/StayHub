from datetime import date, timedelta
from decimal import Decimal

from app.services.pricing import calculate_room_price


def build_daily_rate_breakdown(
    check_in: date,
    check_out: date,
    rows: dict,
    discount_percent: Decimal = Decimal("0"),
    tax_percent: Decimal = Decimal("0"),
) -> list[dict]:
    """Build one pricing record per occupied night using that night's calendar rate."""
    result = []
    current = check_in
    while current < check_out:
        row = rows.get(current)
        rate = Decimal(str(row.get("rate", 0) if row else 0))
        pricing = calculate_room_price(rate, discount_percent, tax_percent)
        result.append({
            "date": current,
            "base_price": pricing.base_price,
            "discount_percent": pricing.discount_percent,
            "discount_amount": pricing.discount_amount,
            "selling_price": pricing.selling_price,
            "tax_percent": pricing.tax_percent,
            "tax_amount": pricing.tax_amount,
            "total_price": pricing.total_price,
        })
        current += timedelta(days=1)
    return result
