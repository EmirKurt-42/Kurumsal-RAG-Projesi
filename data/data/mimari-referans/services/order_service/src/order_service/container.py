"""Composition root: where abstractions meet implementations.

This service owns two long-lived resources: the database engine and a
single shared httpx client for calls to user_service (connection pooling —
opening a fresh client per request would defeat keep-alive).
"""

import httpx

from order_service.infrastructure.config import Settings
from order_service.infrastructure.database.session import Database


class Container:
    """Holds the long-lived resources of one application instance."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.database_url, echo=settings.debug)
        self.http_client = httpx.AsyncClient(
            base_url=settings.user_service_url,
            timeout=settings.user_service_timeout_seconds,
        )

    async def startup(self) -> None:
        await self.database.create_schema()

    async def shutdown(self) -> None:
        await self.http_client.aclose()
        await self.database.dispose()
