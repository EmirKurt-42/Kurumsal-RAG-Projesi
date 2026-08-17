"""Shared fixtures for order_service tests.

The integration client swaps the real HTTP gateway for a fake via
``app.dependency_overrides`` — the documented FastAPI seam for replacing a
dependency. Everything else (routing, validation, ORM, transactions) stays
real.
"""

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from order_service.api.dependencies import get_user_gateway
from order_service.container import Container
from order_service.infrastructure.config import Settings
from order_service.main import create_app
from tests.unit.application.fakes import FakeUserGateway


@pytest.fixture
def known_user_id() -> UUID:
    """A user id the fake gateway will report as existing."""
    return uuid4()


@pytest.fixture
async def client(known_user_id: UUID) -> AsyncIterator[AsyncClient]:
    """HTTP client bound to an app with in-memory SQLite and a fake gateway."""
    settings = Settings(database_url="sqlite+aiosqlite:///:memory:")
    container = Container(settings)
    await container.startup()

    app = create_app(container)
    app.dependency_overrides[get_user_gateway] = lambda: FakeUserGateway({known_user_id})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    await container.shutdown()
