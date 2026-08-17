"""RegisterUser use case — tested without FastAPI or a database."""

import pytest

from tests.unit.application.fakes import InMemoryUserRepository
from user_service.application.dto import RegisterUserInput
from user_service.application.use_cases.register_user import RegisterUser
from user_service.domain.exceptions import EmailAlreadyRegisteredError


async def test_registers_a_new_user() -> None:
    users = InMemoryUserRepository()
    use_case = RegisterUser(users)

    output = await use_case.execute(
        RegisterUserInput(email="Ada@Example.com", full_name="Ada Lovelace")
    )

    assert output.email == "ada@example.com"  # normalised by the Email value object
    assert await users.get(output.id) is not None  # persisted through the port


async def test_rejects_duplicate_email_case_insensitively() -> None:
    users = InMemoryUserRepository()
    use_case = RegisterUser(users)
    await use_case.execute(RegisterUserInput(email="ada@example.com", full_name="Ada"))

    with pytest.raises(EmailAlreadyRegisteredError):
        await use_case.execute(RegisterUserInput(email="ADA@example.com", full_name="Imposter"))
