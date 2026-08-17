"""End-to-end API tests: real HTTP layer, real (in-memory) database.

Complements the unit tests: those prove the logic, these prove the wiring —
routing, validation, dependency injection, ORM mapping and error handling.
"""

from httpx import AsyncClient


async def test_register_and_fetch_user(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/users",
        json={"email": "ada@example.com", "full_name": "Ada Lovelace"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["email"] == "ada@example.com"
    assert body["is_active"] is True

    fetched = await client.get(f"/api/v1/users/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Ada Lovelace"


async def test_lists_users_newest_first(client: AsyncClient) -> None:
    for email in ("first@example.com", "second@example.com"):
        response = await client.post(
            "/api/v1/users", json={"email": email, "full_name": "Test User"}
        )
        assert response.status_code == 201

    listed = await client.get("/api/v1/users")
    assert listed.status_code == 200
    assert [u["email"] for u in listed.json()] == ["second@example.com", "first@example.com"]


async def test_duplicate_email_maps_to_409(client: AsyncClient) -> None:
    payload = {"email": "grace@example.com", "full_name": "Grace Hopper"}
    assert (await client.post("/api/v1/users", json=payload)).status_code == 201
    assert (await client.post("/api/v1/users", json=payload)).status_code == 409


async def test_unknown_user_maps_to_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_invalid_email_maps_to_422(client: AsyncClient) -> None:
    # Rejected by the domain (Email value object), not by Pydantic.
    response = await client.post(
        "/api/v1/users", json={"email": "not-an-email", "full_name": "X"}
    )
    assert response.status_code == 422


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
