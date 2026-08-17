"""The ``User`` entity — aggregate root of this service."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from user_service.domain.exceptions import InvalidFullNameError
from user_service.domain.value_objects.email import Email


@dataclass(slots=True)
class User:
    """A registered user of the platform.

    ``User`` is an *entity*: it has a stable identity (``id``) while its
    other attributes may change over time. New instances are created through
    the :meth:`register` factory so that every ``User`` in the system
    satisfies the registration invariants — reconstructing an existing user
    from storage (see the repository adapter) bypasses the factory on
    purpose, because those invariants were enforced when it was first
    created.
    """

    id: uuid.UUID
    email: Email
    full_name: str
    is_active: bool
    created_at: datetime

    @classmethod
    def register(cls, *, email: Email, full_name: str) -> "User":
        """Create a brand-new user, enforcing all registration rules.

        Rules enforced here (e-mail validity lives in :class:`Email`):
        - the full name must not be blank,
        - consecutive whitespace in the name is collapsed.
        """
        cleaned_name = " ".join(full_name.split())
        if not cleaned_name:
            raise InvalidFullNameError()
        return cls(
            id=uuid.uuid4(),
            email=email,
            full_name=cleaned_name,
            is_active=True,
            created_at=datetime.now(UTC),
        )
