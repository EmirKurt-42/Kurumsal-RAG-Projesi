"""Money value object — pure domain tests."""

from decimal import Decimal

import pytest

from order_service.domain.exceptions import CurrencyMismatchError, InvalidAmountError
from order_service.domain.value_objects.money import Money


def test_normalizes_to_two_decimal_places() -> None:
    assert Money(Decimal("79.9")).amount == Decimal("79.90")


def test_adds_amounts_in_the_same_currency() -> None:
    total = Money(Decimal("10.50")) + Money(Decimal("5.25"))
    assert total == Money(Decimal("15.75"))


def test_multiplies_by_quantity() -> None:
    assert Money(Decimal("79.90")).multiply(2).amount == Decimal("159.80")


def test_refuses_to_mix_currencies() -> None:
    with pytest.raises(CurrencyMismatchError):
        Money(Decimal("10"), "TRY") + Money(Decimal("10"), "USD")


def test_rejects_negative_amounts() -> None:
    with pytest.raises(InvalidAmountError):
        Money(Decimal("-1"))


def test_currency_is_normalized_to_uppercase() -> None:
    assert Money(Decimal("1"), "try").currency == "TRY"
