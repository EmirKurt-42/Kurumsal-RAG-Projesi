"""Use case: list all registered users."""

from user_service.application.dto import UserOutput
from user_service.application.ports.user_repository import UserRepository


class ListUsers:
    """Return every user, newest first.

    Deliberately unpaginated to stay minimal — adding ``limit``/``offset``
    through all layers is a suggested exercise (see docs/service-overview.md).
    """

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self) -> list[UserOutput]:
        users = await self._users.list_all()
        return [UserOutput.from_entity(user) for user in users]
