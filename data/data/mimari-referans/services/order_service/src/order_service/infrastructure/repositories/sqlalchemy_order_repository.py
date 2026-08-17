"""Adapter: SQLAlchemy implementation of the ``OrderRepository`` port."""

from datetime import UTC
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.application.ports.order_repository import OrderRepository
from order_service.domain.entities.order import Order, OrderItem, OrderStatus
from order_service.domain.value_objects.money import Money
from order_service.infrastructure.database.models import OrderItemModel, OrderModel


class SqlAlchemyOrderRepository(OrderRepository):
    """Persists the ``Order`` aggregate in a relational database.

    Translates in both directions between the aggregate (``Order`` +
    ``OrderItem`` + ``Money``) and its two-table row shape. The aggregate
    is always written and read as a whole.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> None:
        self._session.add(self._to_row(order))
        await self._session.flush()

    async def get(self, order_id: UUID) -> Order | None:
        row = await self._session.get(OrderModel, str(order_id))
        return self._to_entity(row) if row is not None else None

    async def list_by_user(self, user_id: UUID) -> list[Order]:
        statement = (
            select(OrderModel)
            .where(OrderModel.user_id == str(user_id))
            .order_by(OrderModel.created_at.desc())
        )
        rows = (await self._session.execute(statement)).scalars().all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_row(order: Order) -> OrderModel:
        return OrderModel(
            id=str(order.id),
            user_id=str(order.user_id),
            status=order.status.value,
            currency=order.total.currency,
            created_at=order.created_at,
            items=[
                OrderItemModel(
                    product_name=item.product_name,
                    unit_price=str(item.unit_price.amount),
                    quantity=item.quantity,
                )
                for item in order.items
            ],
        )

    @staticmethod
    def _to_entity(row: OrderModel) -> Order:
        # SQLite discards timezone info; normalise back to UTC on the way out.
        created_at = (
            row.created_at if row.created_at.tzinfo else row.created_at.replace(tzinfo=UTC)
        )
        return Order(
            id=UUID(row.id),
            user_id=UUID(row.user_id),
            items=tuple(
                OrderItem(
                    product_name=item.product_name,
                    unit_price=Money(Decimal(item.unit_price), row.currency),
                    quantity=item.quantity,
                )
                for item in row.items
            ),
            status=OrderStatus(row.status),
            created_at=created_at,
        )
