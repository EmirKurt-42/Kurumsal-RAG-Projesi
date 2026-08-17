"""Use case: fetch a single user by id."""

from uuid import UUID

from user_service.application.dto import UserOutput
from user_service.application.ports.user_repository import UserRepository
from user_service.domain.exceptions import UserNotFoundError


class GetUser:
    """Return one user or raise ``UserNotFoundError``.

    Note that "absent" is expressed as ``None`` by the repository but as an
    exception by the use case: the port reports facts, the application
    decides what a missing user *means* for this workflow.
    """

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self, user_id: UUID) -> UserOutput:
        user = await self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(str(user_id))
        return UserOutput.from_entity(user)
