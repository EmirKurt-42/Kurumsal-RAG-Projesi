"""Domain-level errors for the order service.

Business-language exceptions; the api layer maps them to HTTP status codes
in ``api/exception_handlers.py``. Note that "user service is unreachable"
is *not* here — that is an orchestration failure and lives in
``application/exceptions.py``.
"""

from decimal import Decimal


class DomainError(Exception):
    """Base class for every domain error of this service."""


class OrderNotFoundError(DomainError):
    """Raised when an order id does not resolve to an existing order."""

    def __init__(self, order_id: str) -> None:
        super().__init__(f"Order '{order_id}' does not exist.")


class UserNotFoundError(DomainError):
    """Raised when an order references a user that does not exist."""

    def __init__(self, user_id: str) -> None:
        super().__init__(f"User '{user_id}' does not exist or is inactive.")


class EmptyOrderError(DomainError):
    """Raised when an order is created without any items."""

    def __init__(self) -> None:
        super().__init__("An order must contain at least one item.")


class InvalidQuantityError(DomainError):
    """Raised when an order item has a non-positive quantity."""

    def __init__(self, product_name: str, quantity: int) -> None:
        super().__init__(
            f"Quantity for '{product_name}' must be positive, got {quantity}."
        )


class InvalidAmountError(DomainError):
    """Raised when a monetary amount is negative."""

    def __init__(self, amount: Decimal) -> None:
        super().__init__(f"A monetary amount cannot be negative, got {amount}.")


class CurrencyMismatchError(DomainError):
    """Raised when arithmetic mixes two different currencies."""

    def __init__(self, left: str, right: str) -> None:
        super().__init__(f"Cannot combine amounts in {left} and {right}.")
