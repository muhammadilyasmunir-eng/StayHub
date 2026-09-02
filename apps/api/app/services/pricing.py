from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


TWOPLACES = Decimal("0.01")


@dataclass(frozen=True)
class RoomPrice:
    base_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    selling_price: Decimal
    tax_percent: Decimal
    tax_amount: Decimal
    total_price: Decimal


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def property_billing_is_configured(hotel) -> bool:
    """Return True only when both property-level billing rates are explicitly set."""
    return hotel.tax_percent is not None and hotel.commission_percent is not None


def calculate_room_price(
    base_price: Decimal,
    discount_percent: Decimal = Decimal("0"),
    tax_percent: Decimal = Decimal("0"),
) -> RoomPrice:
    base = money(Decimal(base_price))
    discount_pct = Decimal(discount_percent)
    tax_pct = Decimal(tax_percent)

    if base < 0:
        raise ValueError("base_price cannot be negative")
    if not Decimal("0") <= discount_pct <= Decimal("100"):
        raise ValueError("discount_percent must be between 0 and 100")
    if not Decimal("0") <= tax_pct <= Decimal("100"):
        raise ValueError("tax_percent must be between 0 and 100")

    discount_amount = money(base * discount_pct / Decimal("100"))
    selling_price = money(base - discount_amount)
    tax_amount = money(selling_price * tax_pct / Decimal("100"))
    total_price = money(selling_price + tax_amount)

    return RoomPrice(
        base_price=base,
        discount_percent=discount_pct,
        discount_amount=discount_amount,
        selling_price=selling_price,
        tax_percent=tax_pct,
        tax_amount=tax_amount,
        total_price=total_price,
    )
