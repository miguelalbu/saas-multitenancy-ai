"""Multi-tenant isolation tests (Pillar 1) — critical for security review."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_org_a_cannot_see_org_b_tasks(client, make_org):
    org_a = await make_org("Acme Corp")
    org_b = await make_org("Globex Inc")

    await client.post(
        "/v1/tasks", headers=org_a.admin_headers, json={"title": "Acme secret"}
    )
    await client.post(
        "/v1/tasks", headers=org_b.admin_headers, json={"title": "Globex secret"}
    )

    resp_a = await client.get("/v1/tasks", headers=org_a.admin_headers)
    titles_a = [t["title"] for t in resp_a.json()["items"]]
    assert titles_a == ["Acme secret"]

    resp_b = await client.get("/v1/tasks", headers=org_b.admin_headers)
    titles_b = [t["title"] for t in resp_b.json()["items"]]
    assert titles_b == ["Globex secret"]


@pytest.mark.asyncio
async def test_org_a_cannot_access_org_b_task_by_id(client, make_org):
    org_a = await make_org("Acme Corp")
    org_b = await make_org("Globex Inc")

    created_b = await client.post(
        "/v1/tasks", headers=org_b.admin_headers, json={"title": "Globex only"}
    )
    task_b_id = created_b.json()["id"]

    # Org A tries to read Org B's task by its real ID -> must be 404, not 403,
    # so the existence of the resource is not leaked across tenants.
    resp = await client.get(
        f"/v1/tasks/{task_b_id}", headers=org_a.admin_headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_a_cannot_delete_org_b_task(client, make_org):
    org_a = await make_org("Acme Corp")
    org_b = await make_org("Globex Inc")

    created_b = await client.post(
        "/v1/tasks", headers=org_b.admin_headers, json={"title": "Globex only"}
    )
    task_b_id = created_b.json()["id"]

    resp = await client.delete(
        f"/v1/tasks/{task_b_id}", headers=org_a.admin_headers
    )
    assert resp.status_code == 404

    # And the task still exists for its real owner.
    still_there = await client.get(
        f"/v1/tasks/{task_b_id}", headers=org_b.admin_headers
    )
    assert still_there.status_code == 200


@pytest.mark.asyncio
async def test_unknown_task_id_returns_404(client, make_org):
    org = await make_org("Acme Corp")
    resp = await client.get(
        f"/v1/tasks/{uuid.uuid4()}", headers=org.admin_headers
    )
    assert resp.status_code == 404
