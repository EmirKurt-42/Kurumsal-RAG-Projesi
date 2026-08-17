"""Port: persistence contract required by the use cases."""

from abc import ABC, abstractmethod
from uuid import UUID

from user_service.domain.entities.user import User
from user_service.domain.value_objects.email import Email


class UserRepository(ABC):
    """Persistence boundary for ``User`` entities.

    Use cases program against this interface and never learn which
    technology sits behind it. The SQLAlchemy adapter lives in
    ``infrastructure/repositories``; tests substitute an in-memory fake.
    Methods speak in domain terms (entities, value objects) — no rows,
    no sessions, no SQL leaks through this boundary.
    """

    @abstractmethod
    async def add(self, user: User) -> None:
        """Persist a new user."""

    @abstractmethod
    async def get(self, user_id: UUID) -> User | None:
        """Return the user with ``user_id``, or ``None`` if absent."""

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Return the user owning ``email``, or ``None`` if absent."""

    @abstractmethod
    async def list_all(self) -> list[User]:
        """Return every user, newest first."""
