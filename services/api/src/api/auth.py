"""Auth endpoints: register, login, status, refresh, logout."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel

from src.api.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    hash_password,
)
from src.api.users import crud
from src.api.users.models import User, UserCreate, UserRead
from src.config import Settings, get_settings
from src.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"
REFRESH_COOKIE_PATH = "/auth"


class LoginRequest(SQLModel):
    email: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


def _set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    # httpOnly so JS can't read it; scoped to /auth; secure only in production so
    # the dev/test client over http still receives it.
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    try:
        return crud.create_user(session, user)
    except IntegrityError:
        session.rollback()
        # Generic message so the response doesn't confirm which field already exists.
        raise HTTPException(status_code=400, detail="Could not complete registration")


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Token:
    user = crud.authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    _set_refresh_cookie(response, create_refresh_token(user, settings), settings)
    return Token(access_token=create_access_token(user, settings), token_type="bearer")


@router.post("/refresh", response_model=Token)
def refresh(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
    refresh_token: str | None = Cookie(default=None),
) -> Token:
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    user_id = decode_refresh_token(refresh_token, settings)
    user = crud.get_user_by_id(session, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return Token(access_token=create_access_token(user, settings), token_type="bearer")


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)
    return {"message": "logged out"}


@router.get("/status", response_model=UserRead)
def read_status(current_user: User = Depends(get_current_user)) -> User:
    return current_user
