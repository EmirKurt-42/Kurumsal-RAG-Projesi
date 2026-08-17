"""Request/response schemas for the ``/orders`` endpoints."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderItemRequest(BaseModel):
    """One requested line of a new order.

    Pydantic checks the wire-level shape (positive numbers, two decimal
    places); the *business* invariants are enforced again by the domain —
    the API is just one door into the system, and not necessarily the only
    one.
    """

    product_name: str = Field(min_length=1, max_length=200, examples=["Klavye"])
    unit_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=["79.90"])
    quantity: int = Field(gt=0, examples=[2])


class CreateOrderRequest(BaseModel):
    """Payload for ``POST /orders``."""

    user_id: UUID
    currency: str = Field(default="TRY", min_length=3, max_length=3, examples=["TRY"])
    items: list[OrderItemRequest]


class OrderItemResponse(BaseModel):
    """Public representation of one order line."""

    model_config = ConfigDict(from_attributes=True)

    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class OrderResponse(BaseModel):
    """Public representation of an order."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: str
    currency: str
    total: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
