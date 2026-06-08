"""Authentication and token-handling tests."""

import pytest


@pytest.mark.asyncio
async def test_login_success_returns_token(client, make_org):
    await make_org("Acme Corp")

    resp = await client.post(
        "/v1/auth/login",
        json={"email": "admin@acmecorp.com", "password": "password123"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password_is_rejected(client, make_org):
    await make_org("Acme Corp")

    resp = await client.post(
        "/v1/auth/login",
        json={"email": "admin@acmecorp.com", "password": "wrong"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user_is_rejected(client, make_org):
    await make_org("Acme Corp")

    resp = await client.post(
        "/v1/auth/login",
        json={"email": "ghost@acmecorp.com", "password": "password123"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token(client):
    resp = await client.get("/v1/tasks")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_protected_route_rejects_invalid_token(client):
    resp = await client.get(
        "/v1/tasks", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401
