"""The ``Email`` value object."""

import re
from dataclasses import dataclass

from user_service.domain.exceptions import InvalidEmailError

_EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


@dataclass(frozen=True, slots=True)
class Email:
    """An e-mail address that is guaranteed to be well-formed.

    Value object semantics: immutable, compared by value — two ``Email``
    instances holding the same address are interchangeable. Validation and
    normalisation happen at construction, so an invalid ``Email`` cannot
    exist anywhere in the system. This is why the rest of the codebase can
    pass e-mails around without re-checking them.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_PATTERN.match(normalized):
            raise InvalidEmailError(self.value)
        # frozen=True blocks normal assignment; this is the sanctioned way
        # to normalise a field inside __post_init__.
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
