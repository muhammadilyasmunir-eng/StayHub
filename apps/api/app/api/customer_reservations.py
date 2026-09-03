from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import require_admin, require_customer, require_hotel_owner
from app.models.guest import Guest
from app.models.notification import Notification
from app.models.reservation import Reservation, ReservationStatus
from app.models.reservation_status_dispute import ReservationStatusDispute, ReservationDisputeStatus
from app.models.user import User, UserRole
from app.services.commission_service import sync_commission_status
from app.api.reservation import serialize

router = APIRouter(tags=["Customer Reservations"])

class DisputeCreate(BaseModel):
    reason: str = Field(min_length=10, max_length=2000)

class DisputeResolve(BaseModel):
    decision: str = Field(pattern="^(confirm_guest|reject|close)$")
    note: str | None = Field(default=None, max_length=2000)

def _guest_ids_for_user(db: Session, user: User) -> list[int]:
    return [guest.id for guest in db.query(Guest).filter(Guest.email.ilike(user.email)).all()]

def _reservation_for_customer(db: Session, reservation_id: int, user: User) -> Reservation:
    guest_ids = _guest_ids_for_user(db, user)
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.guest_id.in_(guest_ids)).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")
    return reservation

def _reservation_payload(db: Session, reservation: Reservation):
    commission = sync_commission_status(db, reservation)
    data = serialize(reservation, commission_override=commission, db=db)
    data["hotel_name"] = reservation.hotel.name if reservation.hotel else None
    data["incorrect_status_report_deadline"] = (
        reservation.check_out + timedelta(days=10) if reservation.check_out else None
    )
    data["incorrect_status_report_expired"] = bool(
        reservation.check_out and datetime.now(timezone.utc).replace(tzinfo=None) > reservation.check_out + timedelta(days=10)
    )
    return data

@router.get("/customer/reservations")
def customer_reservations(db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    guest_ids = _guest_ids_for_user(db, current_user)
    if not guest_ids:
        return []
    rows = db.query(Reservation).filter(Reservation.guest_id.in_(guest_ids)).order_by(Reservation.created_at.desc(), Reservation.id.desc()).all()
    result = [_reservation_payload(db, r) for r in rows]
    db.commit()
    return result

@router.get("/customer/reservations/{reservation_id}")
def customer_reservation_detail(reservation_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _reservation_for_customer(db, reservation_id, current_user)
    result = _reservation_payload(db, reservation)
    db.commit()
    return result

@router.get("/customer/reservations/by-confirmation/{confirmation_no}")
def customer_reservation_messages(confirmation_no: str, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    guest_ids = _guest_ids_for_user(db, current_user)
    reservation = db.query(Reservation).filter(Reservation.confirmation_no == confirmation_no, Reservation.guest_id.in_(guest_ids)).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")
    result = _reservation_payload(db, reservation)
    events = [{"title": "Reservation created", "message": f"Reservation #{reservation.confirmation_no} was received by StayHub.", "created_at": reservation.created_at}]
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.hotel_id == reservation.hotel_id).order_by(Notification.created_at.asc()).all()
    for n in notifications:
        if str(reservation.confirmation_no) in (n.message or ""):
            events.append({"title": n.title, "message": n.message, "created_at": n.created_at})
    disputes = db.query(ReservationStatusDispute).filter(ReservationStatusDispute.reservation_id == reservation.id).order_by(ReservationStatusDispute.created_at.asc()).all()
    for d in disputes:
        events.append({"title": "Status report submitted" if d.status == ReservationDisputeStatus.OPEN else "Status report reviewed","message": "Your incorrect-status report is under StayHub Admin review." if d.status == ReservationDisputeStatus.OPEN else ("The hotel owner verified that you stayed. StayHub Admin will close the dispute." if d.status == ReservationDisputeStatus.OWNER_VERIFIED else ("StayHub confirmed the reservation status was corrected to Confirmed." if d.status == ReservationDisputeStatus.RESOLVED_GUEST else "StayHub reviewed the report and did not change the property status.")),"created_at": d.resolved_at or d.created_at})
    events.sort(key=lambda x: str(x.get("created_at") or ""))
    db.commit()
    return {"reservation": result, "events": events}

@router.post("/customer/reservations/{reservation_id}/dispute")
def create_dispute(reservation_id: int, payload: DisputeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    reservation = _reservation_for_customer(db, reservation_id, current_user)
    if reservation.status != ReservationStatus.NO_SHOW:
        raise HTTPException(400, "Only a reservation marked No Show can be reported as incorrect")
    if not reservation.check_out:
        raise HTTPException(400, "This reservation has no check-out date, so the report deadline cannot be determined")
    deadline = reservation.check_out + timedelta(days=10)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now > deadline:
        raise HTTPException(400, "The 10-day time limit has expired. You had 10 days after check-out to report an incorrect reservation status.")
    existing = db.query(ReservationStatusDispute).filter(ReservationStatusDispute.reservation_id == reservation.id, ReservationStatusDispute.status == ReservationDisputeStatus.OPEN).first()
    if existing:
        raise HTTPException(409, "An incorrect-status report is already under review")
    dispute = ReservationStatusDispute(reservation_id=reservation.id, guest_id=reservation.guest_id, original_status=reservation.status.value, guest_reason=payload.reason.strip())
    db.add(dispute)
    db.flush()
    guest_name = f"{reservation.guest.first_name} {reservation.guest.last_name}".strip() if reservation.guest else "Guest"
    check_in = reservation.check_in.strftime("%d %b %Y")
    owner_id = reservation.hotel.owner_id if reservation.hotel else None
    if owner_id:
        db.add(Notification(user_id=owner_id, hotel_id=reservation.hotel_id, title="Guest disputed reservation status", message=f"Reservation #{reservation.confirmation_no} • {guest_name} • Check-in: {check_in} • reported by the guest as incorrectly marked No-show. StayHub Admin will review the case.", type="reservation_status_dispute"))
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    for admin in admins:
        db.add(Notification(user_id=admin.id, hotel_id=reservation.hotel_id, title="Special Notice: Reservation Status Dispute", message=f"Reservation #{reservation.confirmation_no} • {guest_name} • Check-in: {check_in} • guest reports that the property incorrectly marked this reservation as No-show. Please review the dispute.", type="reservation_status_dispute"))
    db.commit()
    db.refresh(dispute)
    return {"message": "Your report has been sent to StayHub Admin for review.", "dispute_id": dispute.id, "status": dispute.status.value}

@router.post("/owner/reservation-disputes/{dispute_id}/verify")
def owner_verify_dispute(dispute_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_hotel_owner)):
    dispute = db.query(ReservationStatusDispute).filter(ReservationStatusDispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    if dispute.status != ReservationDisputeStatus.OPEN:
        raise HTTPException(400, "This dispute is no longer awaiting owner verification")
    reservation = dispute.reservation
    if not reservation.hotel or reservation.hotel.owner_id != current_user.id:
        raise HTTPException(403, "This reservation does not belong to your property")
    deadline = dispute.created_at + timedelta(days=7) if dispute.created_at else None
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if deadline and now > deadline:
        raise HTTPException(400, "The 7-day time limit has expired. You had 7 days to confirm that the guest stayed.")
    if reservation.status != ReservationStatus.NO_SHOW:
        raise HTTPException(400, "Reservation is no longer marked No Show")
    reservation.status = ReservationStatus.CONFIRMED
    dispute.status = ReservationDisputeStatus.OWNER_VERIFIED
    dispute.resolved_by = current_user.id
    dispute.resolved_at = datetime.now(timezone.utc)
    commission = sync_commission_status(db, reservation)
    guest_name = f"{reservation.guest.first_name} {reservation.guest.last_name}".strip() if reservation.guest else "Guest"
    message = f"Reservation #{reservation.confirmation_no} • {guest_name} was verified by the hotel owner as a genuine stay. The reservation is now Confirmed and applicable commission/revenue has been restored. StayHub Admin can close the dispute."
    owner_notice = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.hotel_id == reservation.hotel_id, Notification.type == "reservation_status_dispute", Notification.message.like(f"%Reservation #{reservation.confirmation_no}%")).order_by(Notification.created_at.desc()).first()
    if owner_notice:
        owner_notice.title = "Reservation dispute verified by Owner"
        owner_notice.message = message
        owner_notice.type = "reservation_status_owner_verified"
        owner_notice.read = True
    admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
    for admin in admins:
        db.add(Notification(user_id=admin.id, hotel_id=reservation.hotel_id, title="Reservation dispute verified by Owner", message=message, type="reservation_status_owner_verified"))
    db.add(Notification(user_id=current_user.id, hotel_id=reservation.hotel_id, title="Reservation dispute verified by Owner", message=f"Reservation #{reservation.confirmation_no} was verified as a genuine stay. The reservation is Confirmed and applicable commission/revenue has been restored.", type="reservation_status_owner_verified", read=True))
    if reservation.guest and reservation.guest.email:
        guest_user = db.query(User).filter(User.email.ilike(reservation.guest.email), User.role == UserRole.CUSTOMER).first()
        if guest_user:
            db.add(Notification(user_id=guest_user.id, hotel_id=reservation.hotel_id, title="Your stay was verified by the hotel", message=f"The hotel owner verified that you stayed for reservation #{reservation.confirmation_no}. StayHub Admin will now close the dispute.", type="reservation_status_owner_verified"))
    db.commit()
    db.refresh(reservation)
    return {"message": "Reservation verified by owner. Commission and revenue have been synchronized.", "reservation": serialize(reservation, commission_override=commission, db=db), "dispute_status": dispute.status.value}

@router.get("/admin/reservation-disputes")
def admin_disputes(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    rows = db.query(ReservationStatusDispute).order_by(ReservationStatusDispute.created_at.desc()).all()
    result = []
    for d in rows:
        r = d.reservation
        result.append({"id": d.id, "reservation_id": r.id, "confirmation_no": r.confirmation_no, "property": r.hotel.name if r.hotel else None, "guest_name": f"{d.guest.first_name} {d.guest.last_name}".strip() if d.guest else None, "guest_email": d.guest.email if d.guest else None, "original_status": d.original_status, "reason": d.guest_reason, "status": d.status.value, "owner_verified": d.status == ReservationDisputeStatus.OWNER_VERIFIED, "admin_note": d.admin_note, "created_at": d.created_at, "resolved_at": d.resolved_at, "owner_verification_deadline": d.created_at + timedelta(days=7) if d.created_at else None})
    return result

@router.post("/admin/reservation-disputes/{dispute_id}/resolve")
def resolve_dispute(dispute_id: int, payload: DisputeResolve, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    dispute = db.query(ReservationStatusDispute).filter(ReservationStatusDispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    if payload.decision == "close":
        if dispute.status != ReservationDisputeStatus.OWNER_VERIFIED:
            raise HTTPException(400, "Only an owner-verified dispute can be closed directly")
        reservation = dispute.reservation
        dispute.status = ReservationDisputeStatus.RESOLVED_GUEST
        dispute.admin_note = payload.note.strip() if payload.note else "Closed by StayHub Admin after owner verification."
        dispute.resolved_by = current_user.id
        dispute.resolved_at = datetime.now(timezone.utc)
        if reservation.guest and reservation.guest.email:
            guest_user = db.query(User).filter(User.email.ilike(reservation.guest.email), User.role == UserRole.CUSTOMER).first()
            if guest_user:
                db.add(Notification(user_id=guest_user.id, hotel_id=reservation.hotel_id, title="Reservation dispute closed", message=f"StayHub Admin closed the dispute for reservation #{reservation.confirmation_no} after the hotel owner verified your stay.", type="reservation_status_owner_verified"))
        owner_id = reservation.hotel.owner_id if reservation.hotel else None
        if owner_id:
            db.add(Notification(user_id=owner_id, hotel_id=reservation.hotel_id, title="Reservation dispute closed", message=f"StayHub Admin closed the dispute for reservation #{reservation.confirmation_no} after your owner verification.", type="reservation_status_owner_verified"))
        commission = sync_commission_status(db, reservation)
        db.commit()
        db.refresh(reservation)
        return {"message": "Owner-verified dispute closed", "reservation": serialize(reservation, commission_override=commission, db=db), "dispute_status": dispute.status.value}
    if dispute.status != ReservationDisputeStatus.OPEN:
        raise HTTPException(400, "This dispute has already been reviewed by the owner or resolved")
    reservation = dispute.reservation
    owner_id = reservation.hotel.owner_id if reservation.hotel else None
    if payload.decision == "confirm_guest":
        if reservation.status != ReservationStatus.NO_SHOW:
            raise HTTPException(400, "Reservation is no longer marked No Show")
        reservation.status = ReservationStatus.CONFIRMED
        dispute.status = ReservationDisputeStatus.RESOLVED_GUEST
        title = "StayHub corrected a reservation status"
        message = f"Reservation #{reservation.confirmation_no} was incorrectly marked No-show. StayHub reviewed the guest report and changed the reservation to Confirmed. Applicable commission and revenue have been restored."
        if owner_id:
            db.add(Notification(user_id=owner_id, hotel_id=reservation.hotel_id, title=title, message=message, type="reservation_status_corrected"))
        if reservation.guest and reservation.guest.email:
            guest_user = db.query(User).filter(User.email.ilike(reservation.guest.email), User.role == UserRole.CUSTOMER).first()
            if guest_user:
                db.add(Notification(user_id=guest_user.id, hotel_id=reservation.hotel_id, title="Reservation status corrected", message=f"StayHub reviewed your report for reservation #{reservation.confirmation_no} and corrected the status to Confirmed.", type="reservation_status_corrected"))
        commission = sync_commission_status(db, reservation)
    else:
        dispute.status = ReservationDisputeStatus.REJECTED
        title = "StayHub reviewed a reservation status report"
        message = f"StayHub reviewed the status report for reservation #{reservation.confirmation_no} and did not change the property status."
        if owner_id:
            db.add(Notification(user_id=owner_id, hotel_id=reservation.hotel_id, title=title, message=message, type="reservation_status_reviewed"))
        commission = sync_commission_status(db, reservation)
    dispute.admin_note = payload.note.strip() if payload.note else None
    dispute.resolved_by = current_user.id
    dispute.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(reservation)
    return {"message": "Dispute resolved", "reservation": serialize(reservation, commission_override=commission, db=db), "dispute_status": dispute.status.value}
