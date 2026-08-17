"""Shared fixtures.

Unit tests need nothing from here — that is the point of the ports &
adapters split. Integration fixtures build the *real* application wired
to a throwaway in-memory database.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from user_service.container import Container
from user_service.infrastructure.config import Settings
from user_service.main import create_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client bound to an app instance backed by in-memory SQLite.

    ``ASGITransport`` calls the app in-process (no sockets) and does not
    run the lifespan, so the container is started and stopped by hand.
    """
    settings = Settings(database_url="sqlite+aiosqlite:///:memory:")
    container = Container(settings)
    await container.startup()

    app = create_app(container)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    await container.shutdown()
