"""User-management endpoints: list, get, update (admin), deactivate (admin)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.api.security import admin_required
from src.api.users import crud
from src.api.users.models import User, UserRead, UserUpdate
from src.db import get_session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(admin_required),
) -> list[User]:
    return crud.get_all_users(session)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(admin_required),
) -> User:
    user = crud.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(admin_required),
) -> User:
    data = payload.model_dump(exclude_unset=True)
    try:
        user = crud.update_user(session, user_id, data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already in use")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserRead)
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(admin_required),
) -> User:
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate yourself")
    user = crud.delete_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
