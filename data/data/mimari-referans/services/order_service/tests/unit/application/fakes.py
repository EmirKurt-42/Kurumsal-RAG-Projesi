"""In-memory fakes for the application ports.

``FakeUserGateway`` is the star here: it stands in for an entire remote
microservice. Because ``CreateOrder`` depends on the ``UserGateway``
interface, these tests run with no network and no user_service process.
"""

from uuid import UUID

from order_service.application.exceptions import UserServiceUnavailableError
from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.user_gateway import UserGateway
from order_service.domain.entities.order import Order


class InMemoryOrderRepository(OrderRepository):
    """Dict-backed implementation of the persistence port."""

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}

    async def add(self, order: Order) -> None:
        self._orders[order.id] = order

    async def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)

    async def list_by_user(self, user_id: UUID) -> list[Order]:
        matches = [o for o in self._orders.values() if o.user_id == user_id]
        return sorted(matches, key=lambda o: o.created_at, reverse=True)


class FakeUserGateway(UserGateway):
    """Configurable stand-in for the user service."""

    def __init__(self, existing_users: set[UUID] | None = None, *, available: bool = True) -> None:
        self.existing_users = existing_users or set()
        self.available = available

    async def exists(self, user_id: UUID) -> bool:
        if not self.available:
            raise UserServiceUnavailableError()
        return user_id in self.existing_users
