"""User entity — registration invariants."""

import uuid

import pytest

from user_service.domain.entities.user import User
from user_service.domain.exceptions import InvalidFullNameError
from user_service.domain.value_objects.email import Email


def test_register_creates_active_user_with_identity() -> None:
    user = User.register(email=Email("ada@example.com"), full_name="Ada Lovelace")

    assert isinstance(user.id, uuid.UUID)
    assert user.is_active
    assert user.created_at.tzinfo is not None  # timestamps are always aware


def test_register_collapses_whitespace_in_name() -> None:
    user = User.register(email=Email("ada@example.com"), full_name="  Ada   Lovelace ")
    assert user.full_name == "Ada Lovelace"


def test_register_rejects_blank_name() -> None:
    with pytest.raises(InvalidFullNameError):
        User.register(email=Email("ada@example.com"), full_name="   ")
