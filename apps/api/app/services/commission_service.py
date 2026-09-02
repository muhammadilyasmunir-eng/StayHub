from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_commission import ReservationCommission

DEFAULT_COMMISSION_PERCENT = Decimal("5.00")


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_property_commission_percent(hotel) -> Decimal:
    if hotel.commission_percent is None:
        return DEFAULT_COMMISSION_PERCENT
    return Decimal(str(hotel.commission_percent))


def _zero_commission(entry: ReservationCommission, owner_amount: Decimal) -> ReservationCommission:
    entry.commission_percent = Decimal("0.00")
    entry.commissionable_amount = Decimal("0.00")
    entry.commission_amount = Decimal("0.00")
    entry.owner_amount = money(owner_amount)
    return entry


def _calculate_commission(reservation: Reservation) -> tuple[Decimal, Decimal, Decimal]:
    guest_total = money(Decimal(str(reservation.total_amount or 0)))
    tax_amount = money(Decimal(str(reservation.tax or 0)))
    commissionable = money(max(Decimal("0.00"), guest_total - tax_amount))
    commission_percent = get_property_commission_percent(reservation.hotel)
    commission_amount = money(commissionable * commission_percent / Decimal("100"))
    owner_amount = money(guest_total - commission_amount)
    return commissionable, commission_amount, owner_amount


def _calculate_first_night_commission(reservation: Reservation) -> tuple[Decimal, Decimal, Decimal]:
    nights = max(1, (reservation.check_out - reservation.check_in).days)
    full_commissionable, _, _ = _calculate_commission(reservation)
    first_night_commissionable = money(full_commissionable / Decimal(str(nights)))
    commission_percent = get_property_commission_percent(reservation.hotel)
    commission_amount = money(first_night_commissionable * commission_percent / Decimal("100"))
    guest_total = money(Decimal(str(reservation.total_amount or 0)))
    owner_amount = money(guest_total - commission_amount)
    return first_night_commissionable, commission_amount, owner_amount


def create_commission(db: Session, reservation: Reservation) -> ReservationCommission:
    existing = db.query(ReservationCommission).filter(
        ReservationCommission.reservation_id == reservation.id
    ).first()

    # Cancelled reservations never carry StayHub commission.
    if reservation.status == ReservationStatus.CANCELLED:
        if existing:
            _zero_commission(existing, Decimal(str(reservation.total_amount or 0)))
            existing.status = "VOID"
            db.flush()
            return existing
        entry = ReservationCommission(
            reservation_id=reservation.id,
            commission_percent=Decimal("0.00"),
            commissionable_amount=Decimal("0.00"),
            commission_amount=Decimal("0.00"),
            owner_amount=money(Decimal(str(reservation.total_amount or 0))),
            status="VOID",
        )
        db.add(entry)
        db.flush()
        return entry

    commission_percent = get_property_commission_percent(reservation.hotel)

    # A waived no-show is permanently commission-free until the reservation is explicitly confirmed again.
    if existing and reservation.status == ReservationStatus.NO_SHOW and existing.status == "NO_SHOW_WAIVED":
        _zero_commission(existing, Decimal(str(reservation.total_amount or 0)))
        existing.status = "NO_SHOW_WAIVED"
        db.flush()
        return existing

    commissionable, commission_amount, owner_amount = _calculate_commission(reservation)
    status = "PENDING"
    if existing:
        existing.commission_percent = commission_percent
        existing.commissionable_amount = commissionable
        existing.commission_amount = commission_amount
        existing.owner_amount = owner_amount
        existing.status = status
        db.flush()
        return existing

    entry = ReservationCommission(
        reservation_id=reservation.id,
        commission_percent=commission_percent,
        commissionable_amount=commissionable,
        commission_amount=commission_amount,
        owner_amount=owner_amount,
        status=status,
    )
    db.add(entry)
    db.flush()
    return entry


def apply_no_show_commission(db: Session, reservation: Reservation, waive_fee: bool) -> ReservationCommission:
    entry = db.query(ReservationCommission).filter(
        ReservationCommission.reservation_id == reservation.id
    ).first()
    if entry is None:
        entry = create_commission(db, reservation)

    guest_total = money(Decimal(str(reservation.total_amount or 0)))
    if waive_fee:
        _zero_commission(entry, guest_total)
        entry.status = "NO_SHOW_WAIVED"
    else:
        commission_percent = get_property_commission_percent(reservation.hotel)
        commissionable, commission_amount, _ = _calculate_first_night_commission(reservation)
        entry.commission_percent = commission_percent
        entry.commissionable_amount = commissionable
        entry.commission_amount = commission_amount
        entry.owner_amount = money(guest_total - commission_amount)
        entry.status = "APPLIES"
    db.flush()
    return entry


def sync_commission_status(db: Session, reservation: Reservation) -> ReservationCommission:
    entry = db.query(ReservationCommission).filter(
        ReservationCommission.reservation_id == reservation.id
    ).first()

    # Cancellation is always commission-free, including legacy rows created before this rule.
    if reservation.status == ReservationStatus.CANCELLED:
        if entry is None:
            entry = create_commission(db, reservation)
        else:
            _zero_commission(entry, Decimal(str(reservation.total_amount or 0)))
            entry.status = "VOID"
            db.flush()
        return entry

    # A waived no-show is authoritative until an admin explicitly confirms the reservation again.
    if reservation.status == ReservationStatus.NO_SHOW and entry and entry.status == "NO_SHOW_WAIVED":
        _zero_commission(entry, Decimal(str(reservation.total_amount or 0)))
        entry.status = "NO_SHOW_WAIVED"
        db.flush()
        return entry

    entry = create_commission(db, reservation)
    if reservation.status == ReservationStatus.NO_SHOW:
        commissionable, commission_amount, _ = _calculate_first_night_commission(reservation)
        entry.commission_percent = get_property_commission_percent(reservation.hotel)
        entry.commissionable_amount = commissionable
        entry.commission_amount = commission_amount
        entry.owner_amount = money(Decimal(str(reservation.total_amount or 0)) - commission_amount)
        entry.status = "APPLIES"
    elif reservation.status in [ReservationStatus.CHECKED_OUT, ReservationStatus.CHECKED_IN, ReservationStatus.CONFIRMED]:
        entry.status = "PENDING"
    db.flush()
    return entry
