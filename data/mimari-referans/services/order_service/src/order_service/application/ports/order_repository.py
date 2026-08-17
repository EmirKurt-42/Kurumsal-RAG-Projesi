"""Port: persistence contract required by the use cases."""

from abc import ABC, abstractmethod
from uuid import UUID

from order_service.domain.entities.order import Order


class OrderRepository(ABC):
    """Persistence boundary for the ``Order`` aggregate.

    The repository always loads and saves the aggregate *whole* (order and
    its items together) — callers never manipulate order_items rows
    directly, so the aggregate's invariants cannot be bypassed.
    """

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Persist a new order with all of its items."""

    @abstractmethod
    async def get(self, order_id: UUID) -> Order | None:
        """Return the order with ``order_id``, or ``None`` if absent."""

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[Order]:
        """Return every order of one user, newest first."""
