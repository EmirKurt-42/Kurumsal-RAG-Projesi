"""The ``Money`` value object — currency-safe monetary arithmetic."""

from dataclasses import dataclass
from decimal import Decimal

from order_service.domain.exceptions import CurrencyMismatchError, InvalidAmountError


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in a specific currency.

    Built on ``Decimal`` because binary floats cannot represent values like
    0.1 exactly — ``0.1 + 0.2 != 0.3`` is a classic source of money bugs.
    Amounts are normalised to two decimal places and may not be negative;
    arithmetic across different currencies is refused instead of silently
    producing nonsense.
    """

    amount: Decimal
    currency: str = "TRY"

    def __post_init__(self) -> None:
        quantized = Decimal(self.amount).quantize(Decimal("0.01"))
        if quantized < 0:
            raise InvalidAmountError(quantized)
        object.__setattr__(self, "amount", quantized)
        object.__setattr__(self, "currency", self.currency.upper())

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: int) -> "Money":
        """Scale the amount, e.g. unit price × quantity."""
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
