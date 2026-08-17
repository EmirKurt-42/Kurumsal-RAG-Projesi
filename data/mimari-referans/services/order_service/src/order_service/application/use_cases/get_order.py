"""Use case: fetch a single order by id."""

from uuid import UUID

from order_service.application.dto import OrderOutput
from order_service.application.ports.order_repository import OrderRepository
from order_service.domain.exceptions import OrderNotFoundError


class GetOrder:
    """Return one order or raise ``OrderNotFoundError``."""

    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    async def execute(self, order_id: UUID) -> OrderOutput:
        order = await self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(str(order_id))
        return OrderOutput.from_entity(order)
