"""Domain-level errors for the user service.

These exceptions speak business language and know nothing about HTTP.
The api layer maps them to status codes in ``api/exception_handlers.py`` —
that translation is deliberately kept out of the domain.
"""


class DomainError(Exception):
    """Base class for every domain error of this service."""


class InvalidEmailError(DomainError):
    """Raised when a value cannot be interpreted as an e-mail address."""

    def __init__(self, raw_value: str) -> None:
        super().__init__(f"'{raw_value}' is not a valid e-mail address.")


class InvalidFullNameError(DomainError):
    """Raised when a user's full name is blank."""

    def __init__(self) -> None:
        super().__init__("Full name must not be blank.")


class EmailAlreadyRegisteredError(DomainError):
    """Raised when registering an e-mail that already belongs to a user."""

    def __init__(self, email: str) -> None:
        super().__init__(f"A user with e-mail '{email}' already exists.")


class UserNotFoundError(DomainError):
    """Raised when a user id does not resolve to an existing user."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"User '{user_id}' does not exist.")
