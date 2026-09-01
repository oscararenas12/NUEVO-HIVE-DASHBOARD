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


_dummy_hash: str | None = None


def _get_dummy_hash() -> str:
    """A cached bcrypt hash used to equalize timing when a user is missing."""
    global _dummy_hash
    if _dummy_hash is None:
        from src.api.security import hash_password

        _dummy_hash = hash_password("constant-time-dummy-password")
    return _dummy_hash


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Return the user if active, the email exists, and the password matches; else None.

    Runs a bcrypt verify even when the user is missing/inactive so response timing
    does not reveal whether an account exists (SEC-005).
    """
    from src.api.security import verify_password

    user = get_user_by_email(session, email)
    if user is None or not user.is_active:
        verify_password(password, _get_dummy_hash())
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def update_user(session: Session, user_id: int, data: dict) -> User | None:
    """Apply the given fields to a user and return it, or None if not found."""
    user = get_user_by_id(session, user_id)
    if user is None:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> User | None:
    """Soft-delete: set is_active False. Returns the user, or None if not found."""
    user = get_user_by_id(session, user_id)
    if user is None:
        return None
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
