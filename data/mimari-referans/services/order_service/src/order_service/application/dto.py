"""Data Transfer Objects crossing the application boundary.

Plain dataclasses on purpose — no Pydantic in this layer. ``Decimal`` is
used for money on the way in and out; converting to/from JSON-friendly
types is the api layer's job.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from order_service.domain.entities.order import Order


@dataclass(frozen=True, slots=True)
class OrderItemInput:
    """One requested line of a new order."""

    product_name: str
    unit_price: Decimal
    quantity: int


@dataclass(frozen=True, slots=True)
class CreateOrderInput:
    """Everything a caller must provide to place an order."""

    user_id: UUID
    items: tuple[OrderItemInput, ...]
    currency: str = "TRY"


@dataclass(frozen=True, slots=True)
class OrderItemOutput:
    """Outward-facing view of one order line."""

    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


@dataclass(frozen=True, slots=True)
class OrderOutput:
    """Outward-facing view of an order, with the total already computed."""

    id: UUID
    user_id: UUID
    status: str
    currency: str
    total: Decimal
    items: tuple[OrderItemOutput, ...]
    created_at: datetime

    @classmethod
    def from_entity(cls, order: Order) -> "OrderOutput":
        """Flatten the aggregate into transportable data."""
        return cls(
            id=order.id,
            user_id=order.user_id,
            status=order.status.value,
            currency=order.total.currency,
            total=order.total.amount,
            items=tuple(
                OrderItemOutput(
                    product_name=item.product_name,
                    unit_price=item.unit_price.amount,
                    quantity=item.quantity,
                    subtotal=item.subtotal.amount,
                )
                for item in order.items
            ),
            created_at=order.created_at,
        )
