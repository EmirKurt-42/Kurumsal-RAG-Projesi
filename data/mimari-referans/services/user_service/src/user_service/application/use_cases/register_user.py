"""Use case: register a new user."""

from user_service.application.dto import RegisterUserInput, UserOutput
from user_service.application.ports.user_repository import UserRepository
from user_service.domain.entities.user import User
from user_service.domain.exceptions import EmailAlreadyRegisteredError
from user_service.domain.value_objects.email import Email


class RegisterUser:
    """Application workflow for user registration.

    Pure orchestration: e-mail format rules live in the ``Email`` value
    object, name rules live in ``User.register``, and persistence hides
    behind the ``UserRepository`` port. The one rule that genuinely belongs
    here is *uniqueness* — it needs the repository, so no single entity
    could ever enforce it.
    """

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self, data: RegisterUserInput) -> UserOutput:
        email = Email(data.email)
        if await self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(str(email))

        user = User.register(email=email, full_name=data.full_name)
        await self._users.add(user)
        return UserOutput.from_entity(user)
