"""Tests for the User model and CRUD functions."""

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.users import crud
from src.api.users.models import User


def make_user(**overrides):
    data = {
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": "hashed",
    }
    data.update(overrides)
    return User(**data)


def test_create_user(session):
    user = crud.create_user(session, make_user())
    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"


def test_email_must_be_unique(session):
    crud.create_user(session, make_user(username="a1", email="dup@example.com"))
    with pytest.raises(IntegrityError):
        crud.create_user(session, make_user(username="a2", email="dup@example.com"))


def test_username_must_be_unique(session):
    crud.create_user(session, make_user(username="same", email="one@example.com"))
    with pytest.raises(IntegrityError):
        crud.create_user(session, make_user(username="same", email="two@example.com"))


def test_default_role_is_employee(session):
    user = crud.create_user(session, make_user())
    assert user.role == "employee"


def test_default_is_active_is_true(session):
    user = crud.create_user(session, make_user())
    assert user.is_active is True


def test_created_at_is_set(session):
    user = crud.create_user(session, make_user())
    assert user.created_at is not None


def test_get_user_by_id(session):
    created = crud.create_user(session, make_user())
    found = crud.get_user_by_id(session, created.id)
    assert found is not None
    assert found.id == created.id


def test_get_user_by_id_missing_returns_none(session):
    assert crud.get_user_by_id(session, 999999) is None


def test_get_user_by_email(session):
    crud.create_user(session, make_user(email="findme@example.com"))
    found = crud.get_user_by_email(session, "findme@example.com")
    assert found is not None
    assert found.email == "findme@example.com"


def test_get_all_users(session):
    crud.create_user(session, make_user(username="u1", email="u1@example.com"))
    crud.create_user(session, make_user(username="u2", email="u2@example.com"))
    users = crud.get_all_users(session)
    assert len(users) == 2
