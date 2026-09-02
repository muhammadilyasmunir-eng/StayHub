import os, secrets, smtplib, time
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import create_access_token, hash_password

router = APIRouter(prefix="/public/booking-otp", tags=["Public Booking OTP"])
_CODES: dict[str, dict] = {}
_TTL = 600
CUSTOMER_SESSION_MINUTES = 60  # 1 hour; customer remains logged in until explicit logout or token expiry.

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

def _send(email: str, code: str) -> str:
    host=os.getenv("SMTP_HOST"); user=os.getenv("SMTP_USER"); password=os.getenv("SMTP_PASSWORD")
    port=int(os.getenv("SMTP_PORT","587")); sender=os.getenv("SMTP_FROM") or user
    if not (host and user and password and sender):
        print(f"[StayHub OTP DEV] {email}: {code}")
        return "development"
    msg=EmailMessage(); msg["Subject"]="Your StayHub booking verification code"; msg["From"]=sender; msg["To"]=email
    msg.set_content(f"Your StayHub verification code is {code}. It expires in 10 minutes.")
    with smtplib.SMTP(host,port,timeout=15) as smtp:
        smtp.starttls(); smtp.login(user,password); smtp.send_message(msg)
    return "email"

@router.post("/send")
def send_otp(payload: OTPRequest):
    code=f"{secrets.randbelow(1000000):06d}"; key=payload.email.lower()
    _CODES[key]={"code":code,"expires":time.time()+_TTL,"token":None}
    try: mode=_send(payload.email,code)
    except Exception as exc:
        _CODES.pop(key,None); raise HTTPException(502, f"Unable to send verification email: {exc}")
    return {"message":"Verification code sent","delivery":mode}

@router.post("/verify")
def verify_otp(payload: OTPVerify):
    key=payload.email.lower(); record=_CODES.get(key)
    if not record or record["expires"]<time.time(): raise HTTPException(400,"Verification code expired. Please request a new code.")
    if not secrets.compare_digest(record["code"],payload.code): raise HTTPException(400,"Invalid verification code")
    db=SessionLocal()
    try:
        user=db.query(User).filter(User.email.ilike(payload.email)).first()
        if user is None:
            user=User(email=payload.email.lower(),full_name=payload.email.split("@",1)[0],hashed_password=hash_password(secrets.token_urlsafe(32)),role=UserRole.CUSTOMER)
            db.add(user); db.commit(); db.refresh(user)
        elif user.role != UserRole.CUSTOMER:
            raise HTTPException(403,"This email belongs to a non-customer account. Please use the appropriate portal login.")
        access_token=create_access_token({"sub":user.email,"role":user.role.value}, expires_minutes=CUSTOMER_SESSION_MINUTES)
        otp_token=secrets.token_urlsafe(32)
        record["token"]=otp_token; record["expires"]=time.time()+_TTL
        return {"verified":True,"access_token":access_token,"otp_token":otp_token,"token_type":"bearer","role":"customer","session_minutes":60}
    finally:
        db.close()

def is_verified(email: str, token: str | None) -> bool:
    record=_CODES.get((email or "").lower())
    return bool(record and record["expires"]>=time.time() and token and record.get("token") and secrets.compare_digest(record["token"],token))


def send_booking_confirmation(email: str, confirmation_no: str, hotel_name: str, room_name: str, check_in, check_out, total) -> bool:
    host=os.getenv("SMTP_HOST"); user=os.getenv("SMTP_USER"); password=os.getenv("SMTP_PASSWORD")
    port=int(os.getenv("SMTP_PORT","587")); sender=os.getenv("SMTP_FROM") or user
    if not (host and user and password and sender):
        print(f"[StayHub booking confirmation DEV] {email}: {confirmation_no}")
        return False
    msg=EmailMessage(); msg["Subject"]=f"StayHub booking confirmed - {confirmation_no}"; msg["From"]=sender; msg["To"]=email
    msg.set_content(f"Your booking is confirmed.\n\nConfirmation: {confirmation_no}\nHotel: {hotel_name}\nRoom: {room_name}\nCheck-in: {check_in}\nCheck-out: {check_out}\nTotal: PKR {total}\n\nThank you for booking with StayHub.")
    with smtplib.SMTP(host,port,timeout=15) as smtp:
        smtp.starttls(); smtp.login(user,password); smtp.send_message(msg)
    return True
