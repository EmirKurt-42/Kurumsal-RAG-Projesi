"""Adapter: httpx implementation of the ``UserGateway`` port."""

from uuid import UUID

import httpx

from order_service.application.exceptions import UserServiceUnavailableError
from order_service.application.ports.user_gateway import UserGateway


class HttpUserGateway(UserGateway):
    """Asks the user service over HTTP whether a user exists.

    The use case only ever sees the ``UserGateway`` interface — swapping
    this adapter for gRPC, a message queue or a cache would not touch a
    single line of application code. Network failures are translated into
    the application-level ``UserServiceUnavailableError``: httpx exceptions
    must not leak through the port.
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        # The client (base_url, timeout) is configured by the container.
        self._client = client

    async def exists(self, user_id: UUID) -> bool:
        try:
            response = await self._client.get(f"/api/v1/users/{user_id}")
            if response.status_code == httpx.codes.NOT_FOUND:
                return False
            response.raise_for_status()
            payload: dict[str, object] = response.json()
            return bool(payload.get("is_active", False))
        except httpx.HTTPError as exc:
            raise UserServiceUnavailableError() from exc
