from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import require_admin
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_commission import ReservationCommission
from app.models.user import User
from app.services.commission_service import sync_commission_status

router = APIRouter(prefix="/finance", tags=["Finance"])


def _commission_count(reservation: Reservation, commission: ReservationCommission | None) -> int:
    if not commission or commission.status in {"VOID", "NO_SHOW_WAIVED"}:
        return 0
    if reservation.status == ReservationStatus.NO_SHOW:
        return 1 if commission.status == "APPLIES" and commission.commission_amount > 0 else 0
    if reservation.status in [ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN, ReservationStatus.CHECKED_OUT]:
        return max(0, (reservation.check_out - reservation.check_in).days)
    return 0


def serialize(reservation: Reservation, commission: ReservationCommission | None):
    nights = max(1, (reservation.check_out - reservation.check_in).days)
    selling_price = Decimal(str(reservation.room_rate or 0)) * nights
    discount_amount = Decimal(str(reservation.discount or 0))
    base_price = selling_price + discount_amount
    tax_amount = Decimal(str(reservation.tax or 0))
    total_amount = Decimal(str(reservation.total_amount or 0))
    return {
        "reservation_id": reservation.id, "confirmation_no": reservation.confirmation_no,
        "hotel_id": reservation.hotel_id, "hotel_name": reservation.hotel.name if reservation.hotel else None,
        "guest_id": reservation.guest_id, "room_id": reservation.room_id,
        "booking_source": reservation.booking_source.value, "check_in": reservation.check_in,
        "check_out": reservation.check_out, "status": reservation.status.value,
        "base_price": base_price,
        "discount_amount": discount_amount,
        "selling_price": selling_price,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "commission_percent": Decimal(str(commission.commission_percent if commission else 0)),
        "commission_amount": Decimal(str(commission.commission_amount if commission else 0)),
        "owner_amount": Decimal(str(commission.owner_amount if commission else total_amount)),
        "commission_status": commission.status if commission else "NOT_CREATED",
        "commission_count": _commission_count(reservation, commission),
    }


def _rows(db: Session, reservations):
    rows=[]
    for reservation in reservations:
        commission = sync_commission_status(db, reservation)
        rows.append(serialize(reservation, commission))
    db.commit()
    return rows


@router.get("/owner/{hotel_id}")
def owner_finance(hotel_id: int, db: Session = Depends(get_db)):
    reservations = db.query(Reservation).filter(Reservation.hotel_id == hotel_id).order_by(Reservation.id.desc()).all()
    rows = _rows(db, reservations)
    return {
        "hotel_id": hotel_id,
        "reservations": rows,
        "total_sales": sum((r["total_amount"] for r in rows), Decimal("0.00")),
        "total_commission": sum((r["commission_amount"] for r in rows if r["commission_status"] != "VOID"), Decimal("0.00")),
        "commission_count": sum(r["commission_count"] for r in rows),
        "owner_earnings": sum((r["owner_amount"] for r in rows if r["commission_status"] != "VOID"), Decimal("0.00")),
    }


@router.get("/admin")
def admin_finance(
    checkout_before: date | None = Query(default=None, description="Only include stays whose checkout date is on/before this date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    cutoff = checkout_before or date.today()
    reservations = db.query(Reservation).filter(Reservation.check_out <= cutoff, Reservation.status.in_([ReservationStatus.CHECKED_OUT, ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN])).order_by(Reservation.check_out.desc(), Reservation.id.desc()).all()
    rows = _rows(db, reservations)
    return {
        "as_of": cutoff,
        "basis": "checkout_date",
        "reservations": rows,
        "total_sales": sum((r["total_amount"] for r in rows), Decimal("0.00")),
        "total_commission": sum((r["commission_amount"] for r in rows if r["commission_status"] != "VOID"), Decimal("0.00")),
        "commission_count": sum(r["commission_count"] for r in rows),
        "total_owner_earnings": sum((r["owner_amount"] for r in rows if r["commission_status"] != "VOID"), Decimal("0.00")),
    }
