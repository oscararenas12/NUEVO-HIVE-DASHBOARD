"""Security helpers: password hashing, JWT tokens, and the current-user dependency."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session

from src.api.users import crud
from src.api.users.models import User
from src.config import Settings, get_settings
from src.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenUrl documents where clients obtain a token (used by Swagger's Authorize).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user: User, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user.id), "role": user.role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _credentials_exception

    user = crud.get_user_by_id(session, user_id)
    if user is None or not user.is_active:
        raise _credentials_exception
    return user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that allows only admin users through (403 otherwise)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
