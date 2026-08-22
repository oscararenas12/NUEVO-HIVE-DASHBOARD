"""Auth endpoints: register, login, status."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel

from src.api.security import create_access_token, get_current_user, hash_password
from src.api.users import crud
from src.api.users.models import User, UserCreate, UserRead
from src.config import Settings, get_settings
from src.db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(SQLModel):
    email: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


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
        raise HTTPException(status_code=400, detail="Username or email already registered")


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Token:
    user = crud.authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user, settings)
    return Token(access_token=token, token_type="bearer")


@router.get("/status", response_model=UserRead)
def read_status(current_user: User = Depends(get_current_user)) -> User:
    return current_user
