from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


class NoShowFeeDecision(str, Enum):
    WAIVE_FEE = "WAIVE_FEE"
    CHARGE_FEE = "CHARGE_FEE"


@dataclass(frozen=True)
class NoShowCommissionResult:
    fee_amount: Decimal
    commission_amount: Decimal
    owner_amount: Decimal
    commission_status: str


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_no_show_commission(
    reservation_total: Decimal,
    commission_percent: Decimal,
    decision: NoShowFeeDecision,
    nights: int = 1,
) -> NoShowCommissionResult:
    total = money(Decimal(reservation_total))
    percent = Decimal(commission_percent)
    if total < 0:
        raise ValueError("reservation_total cannot be negative")
    if not Decimal("0") <= percent <= Decimal("100"):
        raise ValueError("commission_percent must be between 0 and 100")
    if nights < 1:
        raise ValueError("nights must be at least 1")

    if decision == NoShowFeeDecision.WAIVE_FEE:
        return NoShowCommissionResult(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), "VOID")

    # A charged no-show fee is limited to the first night.
    fee_amount = money(total / Decimal(str(nights)))
    commission = money(fee_amount * percent / Decimal("100"))
    owner_amount = money(fee_amount - commission)
    return NoShowCommissionResult(fee_amount, commission, owner_amount, "APPLIES")
