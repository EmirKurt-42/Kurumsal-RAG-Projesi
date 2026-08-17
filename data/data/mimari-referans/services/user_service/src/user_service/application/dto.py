"""Data Transfer Objects crossing the application boundary.

Plain dataclasses on purpose: the application layer must not depend on
Pydantic (an api/infrastructure concern). DTOs carry data across layer
boundaries and never contain behaviour — entities stay inside, DTOs go out.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from user_service.domain.entities.user import User


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    """Everything a caller must provide to register a user."""

    email: str
    full_name: str


@dataclass(frozen=True, slots=True)
class UserOutput:
    """The application layer's outward-facing view of a user."""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserOutput":
        """Flatten a domain entity into transportable data."""
        return cls(
            id=user.id,
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
