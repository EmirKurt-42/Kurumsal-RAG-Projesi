"""In-memory fakes for the application ports.

This file is the payoff of Dependency Inversion: because use cases depend
on the ``UserRepository`` *interface*, tests can substitute this dict-backed
fake and exercise the full application logic without a database.
"""

from uuid import UUID

from user_service.application.ports.user_repository import UserRepository
from user_service.domain.entities.user import User
from user_service.domain.value_objects.email import Email


class InMemoryUserRepository(UserRepository):
    """Dict-backed implementation of the persistence port."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def add(self, user: User) -> None:
        self._users[user.id] = user

    async def get(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: Email) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def list_all(self) -> list[User]:
        return sorted(self._users.values(), key=lambda u: u.created_at, reverse=True)
