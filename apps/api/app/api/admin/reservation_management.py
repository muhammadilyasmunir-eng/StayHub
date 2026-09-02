from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.reservation import serialize
from app.dependencies import get_db, require_admin
from app.models.reservation import ReservationStatus
from app.models.reservation import Reservation
from app.models.room import Room, RoomStatus
from app.schemas.reservation import ReservationDateModification, ReservationNoShowRequest
from app.services.commission_service import sync_commission_status
from app.services.reservation_service import get_reservation_by_id, mark_reservation_no_show, room_is_available

router = APIRouter(prefix="/admin/reservations", tags=["Admin - Reservation Management"])


def _reservation_or_404(db: Session, reservation_id: int) -> Reservation:
    reservation = get_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


def _admin_modify(db: Session, reservation: Reservation, check_in: date, check_out: date):
    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")
    if not room_is_available(db, reservation.room_id, check_in, check_out, reservation.id):
        raise ValueError("Room is already booked for the selected dates")
    nights = (check_out - check_in).days
    reservation.check_in = check_in
    reservation.check_out = check_out
    reservation.total_amount = Decimal(str(reservation.room_rate or 0)) * nights - Decimal(str(reservation.discount or 0)) + Decimal(str(reservation.tax or 0))
    reservation.total_amount = max(reservation.total_amount, Decimal("0.00"))
    commission = sync_commission_status(db, reservation)
    db.commit()
    db.refresh(reservation)
    return reservation, commission


@router.get("/{reservation_id}")
def get_detail(reservation_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    reservation = _reservation_or_404(db, reservation_id)
    commission = sync_commission_status(db, reservation)
    db.commit()
    return serialize(reservation, commission_override=commission, db=db)


@router.post("/{reservation_id}/no-show")
def no_show(reservation_id: int, payload: ReservationNoShowRequest, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    reservation = _reservation_or_404(db, reservation_id)
    if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]:
        raise HTTPException(status_code=400, detail="Reservation cannot be marked no-show in its current status")
    try:
        updated, commission = mark_reservation_no_show(db, reservation, payload.waive_fee)
        return serialize(updated, commission_override=commission, db=db)
    except ValueError:
        # Admin is a platform-level operator and may need to correct a reservation
        # outside the owner action window. Preserve the same commission policy.
        reservation.status = ReservationStatus.NO_SHOW
        room = db.query(Room).filter(Room.id == reservation.room_id).first()
        if room:
            room.status = RoomStatus.AVAILABLE
        from app.services.commission_service import apply_no_show_commission
        commission = apply_no_show_commission(db, reservation, payload.waive_fee)
        db.commit()
        db.refresh(reservation)
        return serialize(reservation, commission_override=commission, db=db)


@router.post("/{reservation_id}/confirm")
def confirm(reservation_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    reservation = _reservation_or_404(db, reservation_id)
    if reservation.status != ReservationStatus.NO_SHOW:
        raise HTTPException(status_code=400, detail="Only a no-show reservation can be confirmed")
    reservation.status = ReservationStatus.CONFIRMED
    commission = sync_commission_status(db, reservation)
    db.commit()
    db.refresh(reservation)
    return serialize(reservation, commission_override=commission, db=db)


@router.post("/{reservation_id}/modify")
def modify(reservation_id: int, payload: ReservationDateModification, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    reservation = _reservation_or_404(db, reservation_id)
    if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]:
        raise HTTPException(status_code=400, detail="This reservation cannot be modified")
    try:
        updated, commission = _admin_modify(db, reservation, payload.check_in, payload.check_out)
        return serialize(updated, commission_override=commission, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{reservation_id}/cancel")
def cancel(reservation_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    reservation = _reservation_or_404(db, reservation_id)
    if reservation.status == ReservationStatus.CANCELLED:
        return serialize(reservation, commission_override=sync_commission_status(db, reservation), db=db)
    reservation.status = ReservationStatus.CANCELLED
    room = db.query(Room).filter(Room.id == reservation.room_id).first()
    if room:
        room.status = RoomStatus.AVAILABLE
    commission = sync_commission_status(db, reservation)
    db.commit()
    db.refresh(reservation)
    return serialize(reservation, commission_override=commission, db=db)
