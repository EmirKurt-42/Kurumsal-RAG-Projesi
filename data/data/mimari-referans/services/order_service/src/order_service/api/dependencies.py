"""FastAPI dependency wiring — request-scoped assembly of use cases.

Integration tests override ``get_user_gateway`` here (via
``app.dependency_overrides``) to replace the real HTTP gateway with a fake:
the whole service is then testable without user_service running.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.user_gateway import UserGateway
from order_service.application.use_cases.create_order import CreateOrder
from order_service.application.use_cases.get_order import GetOrder
from order_service.application.use_cases.list_user_orders import ListUserOrders
from order_service.container import Container
from order_service.infrastructure.gateways.http_user_gateway import HttpUserGateway
from order_service.infrastructure.repositories.sqlalchemy_order_repository import (
    SqlAlchemyOrderRepository,
)


def get_container(request: Request) -> Container:
    """Fetch the application-wide container created in ``main.create_app``."""
    container: Container = request.app.state.container
    return container


async def get_session(
    container: Annotated[Container, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped session: commits on success, rolls back on error."""
    async with container.database.session() as session:
        yield session


def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrderRepository:
    """Bind the ``OrderRepository`` port to its SQLAlchemy adapter."""
    return SqlAlchemyOrderRepository(session)


def get_user_gateway(
    container: Annotated[Container, Depends(get_container)],
) -> UserGateway:
    """Bind the ``UserGateway`` port to its httpx adapter."""
    return HttpUserGateway(container.http_client)


OrderRepositoryDep = Annotated[OrderRepository, Depends(get_order_repository)]
UserGatewayDep = Annotated[UserGateway, Depends(get_user_gateway)]


def get_create_order(orders: OrderRepositoryDep, users: UserGatewayDep) -> CreateOrder:
    return CreateOrder(orders, users)


def get_get_order(orders: OrderRepositoryDep) -> GetOrder:
    return GetOrder(orders)


def get_list_user_orders(orders: OrderRepositoryDep) -> ListUserOrders:
    return ListUserOrders(orders)
