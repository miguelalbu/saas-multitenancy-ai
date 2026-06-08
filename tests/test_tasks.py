"""Task CRUD tests with RBAC enforcement."""

import pytest


@pytest.mark.asyncio
async def test_admin_can_create_task(client, make_org):
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/tasks",
        headers=org.admin_headers,
        json={"title": "Write tests", "priority": "high", "department": "Eng"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Write tests"
    assert body["priority"] == "high"
    assert body["status"] == "pending"
    assert body["organization_id"] == str(org.org_id)


@pytest.mark.asyncio
async def test_member_cannot_create_task(client, make_org):
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/tasks",
        headers=org.member_headers,
        json={"title": "Should fail"},
    )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_member_can_list_tasks(client, make_org):
    org = await make_org("Acme Corp")
    await client.post(
        "/v1/tasks", headers=org.admin_headers, json={"title": "Visible task"}
    )

    resp = await client.get("/v1/tasks", headers=org.member_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Visible task"


@pytest.mark.asyncio
async def test_get_update_delete_flow(client, make_org):
    org = await make_org("Acme Corp")
    created = await client.post(
        "/v1/tasks", headers=org.admin_headers, json={"title": "Lifecycle"}
    )
    task_id = created.json()["id"]

    got = await client.get(f"/v1/tasks/{task_id}", headers=org.admin_headers)
    assert got.status_code == 200

    updated = await client.put(
        f"/v1/tasks/{task_id}",
        headers=org.admin_headers,
        json={"status": "completed"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "completed"

    deleted = await client.delete(
        f"/v1/tasks/{task_id}", headers=org.admin_headers
    )
    assert deleted.status_code == 204

    missing = await client.get(
        f"/v1/tasks/{task_id}", headers=org.admin_headers
    )
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_member_cannot_delete_task(client, make_org):
    org = await make_org("Acme Corp")
    created = await client.post(
        "/v1/tasks", headers=org.admin_headers, json={"title": "Protected"}
    )
    task_id = created.json()["id"]

    resp = await client.delete(
        f"/v1/tasks/{task_id}", headers=org.member_headers
    )
    assert resp.status_code == 403
