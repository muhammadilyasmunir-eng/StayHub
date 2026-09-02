from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.models.reservation import Reservation

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class MessageCreate(BaseModel):
    recipient_user_id: int | None = None
    recipient_email: str | None = None
    reservation_id: int | None = None
    message: str = Field(min_length=1, max_length=4000)

def _reservation_access(db: Session, reservation_id: int | None, user: User, recipient_id: int | None = None):
    if reservation_id is None:
        if user.role != UserRole.ADMIN:
            raise HTTPException(400, "A reservation is required for customer/owner conversations")
        return None
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")
    if user.role == UserRole.HOTEL_OWNER:
        if not reservation.hotel or reservation.hotel.owner_id != user.id:
            raise HTTPException(403, "Reservation does not belong to your property")
    elif user.role == UserRole.CUSTOMER:
        if not reservation.guest or not reservation.guest.email or reservation.guest.email.lower() != user.email.lower():
            raise HTTPException(403, "Reservation does not belong to you")
    if recipient_id:
        recipient = db.query(User).filter(User.id == recipient_id).first()
        if not recipient:
            raise HTTPException(404, "Recipient not found")
        if user.role == UserRole.HOTEL_OWNER and recipient.role == UserRole.CUSTOMER:
            if not reservation.guest or recipient.email.lower() != reservation.guest.email.lower():
                raise HTTPException(403, "Owner can only message the customer of this reservation")
        elif user.role == UserRole.CUSTOMER and recipient.role == UserRole.HOTEL_OWNER:
            if not reservation.hotel or recipient.id != reservation.hotel.owner_id:
                raise HTTPException(403, "Customer can only message the reservation's hotel owner")
        elif user.role != UserRole.ADMIN and recipient.role != UserRole.ADMIN:
            raise HTTPException(403, "This conversation is not allowed")
    return reservation

def _encode_message_type(reservation_id: int | None, sender_id: int, recipient_id: int) -> str:
    return f"message|{reservation_id or 0}|{sender_id}|{recipient_id}"

def _parse_message_type(value: str):
    try:
        kind, rid, sid, tid = value.split("|", 3)
        return (int(rid), int(sid), int(tid)) if kind == "message" else None
    except Exception:
        return None

@router.get("")
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return [{"id":n.id,"title":n.title,"message":n.message,"type":n.type,"read":n.read,"created_at":n.created_at} for n in rows]

@router.get("/messages")
def list_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.type.like("message|%")).order_by(Notification.created_at.asc()).limit(500).all()
    result=[]; cache={}
    for n in rows:
        parsed=_parse_message_type(n.type or "")
        if not parsed: continue
        reservation_id,sender_id,recipient_id=parsed
        if current_user.role != UserRole.ADMIN and current_user.id not in (sender_id,recipient_id): continue
        if sender_id not in cache: cache[sender_id]=db.query(User).filter(User.id==sender_id).first()
        if recipient_id not in cache: cache[recipient_id]=db.query(User).filter(User.id==recipient_id).first()
        sender,recipient=cache[sender_id],cache[recipient_id]
        reservation=db.query(Reservation).filter(Reservation.id==reservation_id).first() if reservation_id else None
        result.append({"id":n.id,"reservation_id":reservation_id or None,"confirmation_no":reservation.confirmation_no if reservation else None,"hotel_id":reservation.hotel_id if reservation else n.hotel_id,"sender_id":sender_id,"sender_name":sender.full_name if sender else f"User #{sender_id}","sender_role":sender.role.value if sender else None,"recipient_id":recipient_id,"recipient_name":recipient.full_name if recipient else f"User #{recipient_id}","recipient_role":recipient.role.value if recipient else None,"message":n.message,"created_at":n.created_at,"read":n.read})
    return result

@router.post("/messages")
def send_message(payload: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipient = None
    if payload.recipient_user_id:
        recipient = db.query(User).filter(User.id == payload.recipient_user_id).first()
    elif payload.recipient_email:
        recipient = db.query(User).filter(User.email.ilike(payload.recipient_email.strip())).first()
    if not recipient: raise HTTPException(404,"Recipient not found")
    if recipient.id == current_user.id: raise HTTPException(400,"You cannot message yourself")
    reservation = _reservation_access(db,payload.reservation_id,current_user,recipient.id)
    if current_user.role == UserRole.CUSTOMER and recipient.role not in (UserRole.HOTEL_OWNER,UserRole.ADMIN):
        raise HTTPException(403,"Customer can message the hotel owner or StayHub Admin")
    if current_user.role == UserRole.HOTEL_OWNER and recipient.role not in (UserRole.CUSTOMER,UserRole.ADMIN):
        raise HTTPException(403,"Owner can message the customer or StayHub Admin")
    hotel_id=reservation.hotel_id if reservation else None
    kind=_encode_message_type(payload.reservation_id,current_user.id,recipient.id)
    now=datetime.now(timezone.utc)
    db.add_all([
        Notification(user_id=recipient.id,hotel_id=hotel_id,title="New message",message=payload.message.strip(),type=kind,read=False,created_at=now),
        Notification(user_id=current_user.id,hotel_id=hotel_id,title="Message sent",message=payload.message.strip(),type=kind,read=True,created_at=now),
    ])
    db.commit()
    return {"sent":True,"reservation_id":payload.reservation_id,"confirmation_no":reservation.confirmation_no if reservation else None}

@router.post("/{notification_id}/read")
def mark_read(notification_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    n=db.query(Notification).filter(Notification.id==notification_id,Notification.user_id==current_user.id).first()
    if not n:return {"updated":False}
    n.read=True;db.commit();return {"updated":True}
