from decimal import Decimal

from app.models.reservation_commission import ReservationCommission
from app.services.commission_service import DEFAULT_COMMISSION_PERCENT, _zero_commission, money


def test_default_commission_is_five_percent_of_pre_tax_selling_price():
    selling_price = Decimal("10000.00")
    tax = Decimal("1600.00")
    total = selling_price + tax
    commissionable = total - tax
    commission = money(commissionable * DEFAULT_COMMISSION_PERCENT / Decimal("100"))
    owner = money(total - commission)

    assert DEFAULT_COMMISSION_PERCENT == Decimal("5.00")
    assert commissionable == Decimal("10000.00")
    assert commission == Decimal("500.00")
    assert owner == Decimal("11100.00")


def test_zero_total_has_zero_commission():
    assert money(Decimal("0") * DEFAULT_COMMISSION_PERCENT / Decimal("100")) == Decimal("0.00")


def test_zero_commission_outcome_clears_percent_and_amounts():
    entry = ReservationCommission(
        reservation_id=1,
        commission_percent=Decimal("15.00"),
        commissionable_amount=Decimal("10000.00"),
        commission_amount=Decimal("1500.00"),
        owner_amount=Decimal("8500.00"),
        status="PENDING",
    )

    _zero_commission(entry, Decimal("12000.00"))

    assert entry.commission_percent == Decimal("0.00")
    assert entry.commissionable_amount == Decimal("0.00")
    assert entry.commission_amount == Decimal("0.00")
    assert entry.owner_amount == Decimal("12000.00")
