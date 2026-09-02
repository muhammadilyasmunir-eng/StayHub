from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.ADMIN:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def require_hotel_owner(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.HOTEL_OWNER:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hotel owner access required",
        )

    return current_user


def require_customer(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role != UserRole.CUSTOMER:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )

    return current_user