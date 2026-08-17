"""Use case: place a new order."""

from order_service.application.dto import CreateOrderInput, OrderOutput
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.user_gateway import UserGateway
from order_service.domain.entities.order import Order, OrderItem
from order_service.domain.exceptions import UserNotFoundError
from order_service.domain.value_objects.money import Money


class CreateOrder:
    """Application workflow for placing an order.

    Reads top-to-bottom like the business would describe it:

    1. the buyer must be a real, active user (asked through the gateway),
    2. the order is assembled under domain rules (``Money``, ``OrderItem``,
       ``Order.create`` enforce their own invariants),
    3. the aggregate is persisted through the repository port.

    Note what is absent: HTTP, SQL, JSON. This class would survive a move
    to a CLI or a message consumer unchanged.
    """

    def __init__(self, orders: OrderRepository, users: UserGateway) -> None:
        self._orders = orders
        self._users = users

    async def execute(self, data: CreateOrderInput) -> OrderOutput:
        if not await self._users.exists(data.user_id):
            raise UserNotFoundError(str(data.user_id))

        items = [
            OrderItem(
                product_name=item.product_name,
                unit_price=Money(item.unit_price, data.currency),
                quantity=item.quantity,
            )
            for item in data.items
        ]
        order = Order.create(user_id=data.user_id, items=items)

        await self._orders.add(order)
        return OrderOutput.from_entity(order)
