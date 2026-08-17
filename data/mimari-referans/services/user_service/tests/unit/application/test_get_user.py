"""GetUser use case."""

from uuid import uuid4

import pytest

from tests.unit.application.fakes import InMemoryUserRepository
from user_service.application.use_cases.get_user import GetUser
from user_service.domain.entities.user import User
from user_service.domain.exceptions import UserNotFoundError
from user_service.domain.value_objects.email import Email


async def test_returns_existing_user() -> None:
    users = InMemoryUserRepository()
    user = User.register(email=Email("ada@example.com"), full_name="Ada Lovelace")
    await users.add(user)

    output = await GetUser(users).execute(user.id)

    assert output.id == user.id
    assert output.full_name == "Ada Lovelace"


async def test_raises_for_unknown_id() -> None:
    with pytest.raises(UserNotFoundError):
        await GetUser(InMemoryUserRepository()).execute(uuid4())
