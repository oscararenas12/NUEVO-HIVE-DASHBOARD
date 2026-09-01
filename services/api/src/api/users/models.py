"""User database model."""

from datetime import datetime
from typing import Literal

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    # Table named "users" (not "user") -- "user" is a reserved word in Postgres.
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="employee")
    is_active: bool = Field(default=True)
    # Set by the database (timezone-aware) so all rows share one clock/source.
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )


class UserCreate(SQLModel):
    """Registration input (plain password, never stored as-is)."""

    username: str
    email: EmailStr
    password: str = Field(min_length=12)


class UserRead(SQLModel):
    """Public user representation -- never includes password_hash."""

    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserUpdate(SQLModel):
    """Admin-editable fields; all optional (only provided fields are changed)."""

    username: str | None = None
    email: EmailStr | None = None
    role: Literal["admin", "employee"] | None = None
    is_active: bool | None = None
