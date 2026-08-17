"""Email value object — pure domain tests: no framework, no database."""

import pytest

from user_service.domain.exceptions import InvalidEmailError
from user_service.domain.value_objects.email import Email


def test_normalizes_case_and_whitespace() -> None:
    assert Email("  Ada@Example.COM ").value == "ada@example.com"


def test_compares_by_value_not_identity() -> None:
    # Value object semantics: same value ⇒ interchangeable instances.
    assert Email("ada@example.com") == Email("ADA@example.com")


@pytest.mark.parametrize("raw", ["", "   ", "not-an-email", "a@b", "@example.com", "ada@"])
def test_rejects_malformed_addresses(raw: str) -> None:
    with pytest.raises(InvalidEmailError):
        Email(raw)
