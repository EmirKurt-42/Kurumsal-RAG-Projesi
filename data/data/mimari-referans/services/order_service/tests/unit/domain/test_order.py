"""Order aggregate — creation invariants and total calculation."""

from decimal import Decimal
from uuid import uuid4

import pytest

from order_service.domain.entities.order import Order, OrderItem, OrderStatus
from order_service.domain.exceptions import EmptyOrderError, InvalidQuantityError
from order_service.domain.value_objects.money import Money


def _item(price: str, quantity: int, name: str = "Klavye") -> OrderItem:
    return OrderItem(product_name=name, unit_price=Money(Decimal(price)), quantity=quantity)


def test_create_starts_pending_and_computes_total() -> None:
    order = Order.create(
        user_id=uuid4(),
        items=[_item("79.90", 2), _item("249.00", 1, name="Mouse")],
    )

    assert order.status is OrderStatus.PENDING
    assert order.total == Money(Decimal("408.80"))  # 2×79.90 + 249.00


def test_create_rejects_empty_orders() -> None:
    with pytest.raises(EmptyOrderError):
        Order.create(user_id=uuid4(), items=[])


def test_item_rejects_non_positive_quantity() -> None:
    with pytest.raises(InvalidQuantityError):
        _item("10.00", 0)


def test_items_are_immutable() -> None:
    # The aggregate exposes items as a tuple: nobody can append a line
    # behind the aggregate's back and corrupt its invariants.
    order = Order.create(user_id=uuid4(), items=[_item("10.00", 1)])
    assert isinstance(order.items, tuple)
