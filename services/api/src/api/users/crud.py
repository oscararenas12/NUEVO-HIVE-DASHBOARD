"""CRUD (create/read) functions for users.

These functions are the single place user rows are read and written -- a
lightweight repository. Endpoints call these rather than touching the DB.
"""

from sqlmodel import Session, select

from src.api.users.models import User


def create_user(session: Session, user: User) -> User:
    """Persist a new user and return it (with DB-populated fields refreshed)."""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_all_users(session: Session) -> list[User]:
    return list(session.exec(select(User)).all())
