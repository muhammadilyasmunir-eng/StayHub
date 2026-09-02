import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.password_reset import PasswordResetToken
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])
RESET_MINUTES = 15
MAX_ATTEMPTS = 5

class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)

class VerifyResetRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str | None = None

GENERIC = "If the account exists, a password reset code has been generated."

def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def _user(db: Session, identifier: str):
    value = identifier.strip()
    return db.query(User).filter((User.email == value) | (User.username == value)).first()

def _cleanup(db: Session):
    now = datetime.now(timezone.utc)
    db.query(PasswordResetToken).filter(PasswordResetToken.expires_at < now).delete(synchronize_session=False)
    db.commit()

@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    _cleanup(db)
    user = _user(db, payload.identifier)
    # Only platform/admin and hotel-owner accounts can use this workflow.
    if user is None or user.role not in (UserRole.ADMIN, UserRole.HOTEL_OWNER):
        return {"message": GENERIC, "reset_token": None}

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": datetime.now(timezone.utc)})
    raw_token = secrets.token_urlsafe(48)
    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_MINUTES),
    )
    db.add(reset)
    db.commit()

    # Email delivery can be wired to SMTP without storing credentials in source.
    # Until SMTP is configured, the token is returned only in debug mode for local development.
    return {"message": GENERIC, "reset_token": raw_token if getattr(__import__('app.core.config', fromlist=['settings']).settings, 'debug', False) else None}

@router.post("/verify-reset", response_model=PasswordResetResponse)
def verify_reset(payload: VerifyResetRequest, db: Session = Depends(get_db)):
    # Kept as a compatibility endpoint; the secure reset token itself is authoritative.
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use the reset token from the password reset request.")

@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == _hash(payload.token),
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > now,
    ).first()
    if reset is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token")
    user = db.query(User).filter(User.id == reset.user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token")
    user.hashed_password = hash_password(payload.new_password)
    reset.used_at = now
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.id != reset.id,
        PasswordResetToken.used_at.is_(None),
    ).update({"used_at": now})
    db.commit()
    return {"message": "Password reset successfully.", "reset_token": None}
