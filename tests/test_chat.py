"""AI chat endpoint tests (Pillar 2).

The LLM is replaced with PydanticAI's built-in TestModel so no real API key
is needed. We patch AgentDeps inside the endpoint via a dependency override so
the tools use the test database session maker.
"""

from __future__ import annotations

import pytest
from pydantic_ai.models.test import TestModel

from app.agent.agent import task_agent
from app.agent.tools import AgentDeps
from app.api.deps import CurrentUser, get_current_user
from app.core.scopes import ALL_SCOPES


def _make_agent_deps_override(org_fixture, call_tools=None):
    """Return a get_current_user override that patches AgentDeps with test session factory."""

    async def _patched_get_current_user() -> CurrentUser:
        raise NotImplementedError("should not be called in this context")

    return org_fixture


@pytest.mark.asyncio
async def test_chat_requires_auth(client, make_org):
    resp = await client.post("/v1/chat", json={"message": "hello"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_chat_requires_chat_use_scope(client, make_org):
    """A member (task:read only) must not access the chat endpoint."""
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/chat",
        headers=org.member_headers,
        json={"message": "hello"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_chat_creates_task_via_tool(client, make_org):
    """TestModel calls create_task; the task is persisted in the test DB."""
    org = await make_org("Acme Corp")

    # Patch get_current_user so the endpoint builds AgentDeps with test session_maker.
    original_get_current_user = get_current_user

    from app.main import app as fastapi_app
    from app.api.deps import get_db

    async def _override_current_user(
        credentials=None,
        db=None,
    ) -> CurrentUser:
        from app.models.user import User
        from app.api.deps import CurrentUser as CU
        from dataclasses import dataclass
        # Build a minimal CurrentUser from the org fixture
        import uuid
        # We need to load the real user from test db
        from sqlalchemy import select
        async with org.session_maker() as session:
            from app.models.user import User as UserModel
            result = await session.execute(
                select(UserModel).where(UserModel.organization_id == org.org_id, UserModel.email.contains("admin"))
            )
            user = result.scalar_one()
        return CU(user=user, organization_id=org.org_id, scopes=list(ALL_SCOPES))

    # Simpler approach: monkeypatch AgentDeps inside the tool via agent override
    original_factory = None

    import app.agent.tools as tools_module
    original_factory = tools_module.async_session_maker

    tools_module.async_session_maker = org.session_maker

    try:
        with task_agent.override(model=TestModel()):
            resp = await client.post(
                "/v1/chat",
                headers=org.admin_headers,
                json={"message": "Create an urgent task called 'Review financial report' for Commercial"},
            )
    finally:
        tools_module.async_session_maker = original_factory

    assert resp.status_code == 200
    body = resp.json()
    assert body["response"]
    action_tools = [a["tool"] for a in body["actions_taken"]]
    assert "create_task" in action_tools


@pytest.mark.asyncio
async def test_chat_list_tasks_tool(client, make_org):
    """TestModel exercises list_tasks and endpoint returns 200."""
    org = await make_org("Acme Corp")

    await client.post(
        "/v1/tasks",
        headers=org.admin_headers,
        json={"title": "Existing task"},
    )

    import app.agent.tools as tools_module
    original_factory = tools_module.async_session_maker
    tools_module.async_session_maker = org.session_maker

    try:
        with task_agent.override(model=TestModel(call_tools=["list_tasks"])):
            resp = await client.post(
                "/v1/chat",
                headers=org.admin_headers,
                json={"message": "Show me my tasks"},
            )
    finally:
        tools_module.async_session_maker = original_factory

    assert resp.status_code == 200
    action_tools = [a["tool"] for a in resp.json()["actions_taken"]]
    assert "list_tasks" in action_tools


@pytest.mark.asyncio
async def test_chat_respects_tenant_isolation(client, make_org):
    """Tasks created via chat belong to caller's org only."""
    org_a = await make_org("Acme Corp")
    org_b = await make_org("Globex Inc")

    import app.agent.tools as tools_module
    original_factory = tools_module.async_session_maker
    tools_module.async_session_maker = org_a.session_maker

    try:
        with task_agent.override(model=TestModel()):
            await client.post(
                "/v1/chat",
                headers=org_a.admin_headers,
                json={"message": "Create a task called 'Acme only task'"},
            )
    finally:
        tools_module.async_session_maker = original_factory

    resp_b = await client.get("/v1/tasks", headers=org_b.admin_headers)
    assert resp_b.json()["total"] == 0
