from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, OwnerRegistration
from app.services.user_service import (
    create_user,
    get_user_by_email,
    authenticate_user,
    create_owner_registration,
)
from app.core.security import create_access_token
from app.dependencies import get_current_user
from app.api.public_booking_otp import is_verified


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return create_user(db, user)


@router.post("/owner-register", status_code=status.HTTP_201_CREATED)
def owner_register(
    registration: OwnerRegistration,
    db: Session = Depends(get_db),
    owner_otp_token: str | None = Header(default=None, alias="X-Owner-OTP-Token"),
):
    if not is_verified(registration.email, owner_otp_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner registration requires a verified email OTP before submission.")
    try:
        owner, hotel = create_owner_registration(db, registration)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return {
        "message": "Complete property registration submitted successfully. Your property is pending StayHub admin approval.",
        "owner": {
            "id": owner.id,
            "email": owner.email,
            "username": owner.username,
            "full_name": owner.full_name,
            "phone": owner.phone,
            "role": owner.role,
        },
        "hotel": {
            "id": hotel.id,
            "property_id": hotel.property_id,
            "name": hotel.name,
            "slug": hotel.slug,
            "status": hotel.status,
        },
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email/username or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
