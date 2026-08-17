"""End-to-end API tests: real HTTP layer, real (in-memory) database.

Only the cross-service gateway is faked (see conftest) — the tests run
without a user_service process, which is exactly what the ``UserGateway``
port buys us.
"""

from decimal import Decimal
from uuid import UUID

from httpx import AsyncClient

from order_service.api.dependencies import get_user_gateway
from tests.unit.application.fakes import FakeUserGateway


def _payload(user_id: UUID) -> dict[str, object]:
    return {
        "user_id": str(user_id),
        "currency": "TRY",
        "items": [
            {"product_name": "Klavye", "unit_price": 79.9, "quantity": 2},
            {"product_name": "Mouse", "unit_price": 249.0, "quantity": 1},
        ],
    }


async def test_create_and_fetch_order(client: AsyncClient, known_user_id: UUID) -> None:
    created = await client.post("/api/v1/orders", json=_payload(known_user_id))
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "pending"
    assert Decimal(str(body["total"])) == Decimal("408.80")
    assert len(body["items"]) == 2

    fetched = await client.get(f"/api/v1/orders/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]


async def test_lists_orders_of_one_user(client: AsyncClient, known_user_id: UUID) -> None:
    for _ in range(2):
        response = await client.post("/api/v1/orders", json=_payload(known_user_id))
        assert response.status_code == 201

    listed = await client.get(f"/api/v1/orders?user_id={known_user_id}")
    assert listed.status_code == 200
    assert len(listed.json()) == 2


async def test_unknown_user_maps_to_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders", json=_payload(UUID("00000000-0000-0000-0000-000000000000"))
    )
    assert response.status_code == 404


async def test_unknown_order_maps_to_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/orders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_empty_items_map_to_422(client: AsyncClient, known_user_id: UUID) -> None:
    response = await client.post(
        "/api/v1/orders",
        json={"user_id": str(known_user_id), "currency": "TRY", "items": []},
    )
    assert response.status_code == 422


async def test_user_service_outage_maps_to_503(client: AsyncClient, known_user_id: UUID) -> None:
    # Re-override the gateway with one that simulates a network failure.
    transport = client._transport  # type: ignore[attr-defined]
    app = transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[get_user_gateway] = lambda: FakeUserGateway(available=False)

    response = await client.post("/api/v1/orders", json=_payload(known_user_id))
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "5"
