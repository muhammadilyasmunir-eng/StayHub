from decimal import Decimal

from app.services.no_show_service import NoShowFeeDecision, calculate_no_show_commission


def test_waive_no_show_fee_voids_commission():
    result = calculate_no_show_commission(Decimal("13153.46"), Decimal("15"), NoShowFeeDecision.WAIVE_FEE)

    assert result.fee_amount == Decimal("0.00")
    assert result.commission_amount == Decimal("0.00")
    assert result.owner_amount == Decimal("0.00")
    assert result.commission_status == "VOID"


def test_charge_no_show_fee_applies_commission_to_fee():
    result = calculate_no_show_commission(Decimal("13153.46"), Decimal("15"), NoShowFeeDecision.CHARGE_FEE)

    assert result.fee_amount == Decimal("13153.46")
    assert result.commission_amount == Decimal("1973.02")
    assert result.owner_amount == Decimal("11180.44")
    assert result.commission_status == "APPLIES"
