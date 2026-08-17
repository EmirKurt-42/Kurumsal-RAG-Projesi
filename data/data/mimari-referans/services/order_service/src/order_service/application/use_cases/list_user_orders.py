"""Use case: list every order belonging to one user."""

from uuid import UUID

from order_service.application.dto import OrderOutput
from order_service.application.ports.order_repository import OrderRepository


class ListUserOrders:
    """Return a user's orders, newest first.

    Deliberately does not verify the user against the gateway: an unknown
    user simply has no orders, and a listing endpoint should not depend on
    another service being up. Compare with ``CreateOrder``, where the check
    protects data integrity and is therefore mandatory.
    """

    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    async def execute(self, user_id: UUID) -> list[OrderOutput]:
        orders = await self._orders.list_by_user(user_id)
        return [OrderOutput.from_entity(order) for order in orders]
