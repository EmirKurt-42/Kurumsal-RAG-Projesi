"""The ``Order`` aggregate: root entity plus its line items."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from order_service.domain.exceptions import EmptyOrderError, InvalidQuantityError
from order_service.domain.value_objects.money import Money


class OrderStatus(StrEnum):
    """Life-cycle states of an order."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class OrderItem:
    """A single line of an order.

    A value object: it has no identity of its own and only exists as part
    of an ``Order``. Its invariant (positive quantity) is checked at
    construction, so an invalid item cannot exist.
    """

    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidQuantityError(self.product_name, self.quantity)

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)


@dataclass(slots=True)
class Order:
    """Aggregate root for orders.

    All access to the line items goes through this class (they are stored
    as an immutable tuple), so the aggregate's invariants hold at every
    moment: an order always has at least one item, and the total is always
    derived from the items — it is never stored, so it can never drift out
    of sync with them.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    items: tuple[OrderItem, ...]
    status: OrderStatus
    created_at: datetime

    @classmethod
    def create(cls, *, user_id: uuid.UUID, items: Sequence[OrderItem]) -> "Order":
        """Place a new order. Domain rule: an order holds at least one item."""
        if not items:
            raise EmptyOrderError()
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            items=tuple(items),
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
        )

    @property
    def total(self) -> Money:
        """Sum of all item subtotals, computed on demand."""
        total = self.items[0].subtotal
        for item in self.items[1:]:
            total = total + item.subtotal
        return total
