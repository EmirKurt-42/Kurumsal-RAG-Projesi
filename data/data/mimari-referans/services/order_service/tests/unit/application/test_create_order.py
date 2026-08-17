"""CreateOrder use case — tested with fakes: no database, no network."""

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from order_service.application.dto import CreateOrderInput, OrderItemInput
from order_service.application.use_cases.create_order import CreateOrder
from order_service.domain.exceptions import EmptyOrderError, UserNotFoundError
from tests.unit.application.fakes import FakeUserGateway, InMemoryOrderRepository


def _input(
    user_id: UUID | None = None,
    items: tuple[OrderItemInput, ...] | None = None,
) -> CreateOrderInput:
    default_items = (
        OrderItemInput(product_name="Klavye", unit_price=Decimal("79.90"), quantity=2),
    )
    return CreateOrderInput(
        user_id=user_id if user_id is not None else uuid4(),
        items=items if items is not None else default_items,
    )


async def test_creates_order_for_existing_user() -> None:
    user_id = uuid4()
    orders = InMemoryOrderRepository()
    use_case = CreateOrder(orders, FakeUserGateway({user_id}))

    output = await use_case.execute(_input(user_id))

    assert output.total == Decimal("159.80")
    assert output.status == "pending"
    assert await orders.get(output.id) is not None  # persisted through the port


async def test_rejects_unknown_user_and_persists_nothing() -> None:
    orders = InMemoryOrderRepository()
    use_case = CreateOrder(orders, FakeUserGateway(set()))
    unknown_user = uuid4()

    with pytest.raises(UserNotFoundError):
        await use_case.execute(_input(unknown_user))

    assert await orders.list_by_user(unknown_user) == []


async def test_rejects_empty_item_list() -> None:
    user_id = uuid4()
    use_case = CreateOrder(InMemoryOrderRepository(), FakeUserGateway({user_id}))

    with pytest.raises(EmptyOrderError):
        await use_case.execute(_input(user_id, items=()))
