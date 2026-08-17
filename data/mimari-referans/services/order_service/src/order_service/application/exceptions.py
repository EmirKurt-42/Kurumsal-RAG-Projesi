"""Application-level errors: failures of orchestration, not of business rules.

"The user service cannot be reached" is not a fact about orders — no
domain expert would utter it — so it does not belong in the domain.
It is a failure of this application's workflow, hence it lives here.
"""


class ApplicationError(Exception):
    """Base class for application-layer failures."""


class UserServiceUnavailableError(ApplicationError):
    """Raised when the user service cannot be reached or misbehaves."""

    def __init__(self) -> None:
        super().__init__("The user service cannot be reached; please try again later.")
