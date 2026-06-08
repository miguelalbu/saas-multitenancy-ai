"""Webhook endpoint and background task tests (Pillar 3)."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.task import TaskStatus
from app.services import webhook_service


@pytest.mark.asyncio
async def test_webhook_returns_202(client, make_org):
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/webhook/event",
        headers=org.admin_headers,
        json={
            "event_type": "financial_alert",
            "organization_id": str(org.org_id),
            "payload": {"message": "Q3 budget exceeded"},
        },
    )

    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_webhook_requires_webhook_manage_scope(client, make_org):
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/webhook/event",
        headers=org.member_headers,
        json={
            "event_type": "financial_alert",
            "organization_id": str(org.org_id),
            "payload": {},
        },
    )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_webhook_invalid_payload_returns_422(client, make_org):
    org = await make_org("Acme Corp")

    resp = await client.post(
        "/v1/webhook/event",
        headers=org.admin_headers,
        json={"bad_field": "no event_type"},
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_webhook_task_overdue_updates_status(make_org, db_session):
    """process_event marks the task overdue and persists it."""
    org = await make_org("Acme Corp")

    # Create a task directly in test DB.
    from app.models.task import Task, TaskPriority, TaskStatus as TS

    task = Task(
        organization_id=org.org_id,
        title="Pending task",
        status=TS.PENDING,
        priority=TaskPriority.MEDIUM,
        created_by=org.admin_id,
    )
    db_session.add(task)
    await db_session.commit()

    import app.services.webhook_service as ws_module
    original = ws_module.async_session_maker
    ws_module.async_session_maker = org.session_maker

    try:
        from app.schemas.webhook import WebhookEvent
        event = WebhookEvent(
            event_type="task_overdue",
            organization_id=org.org_id,
            payload={"task_id": str(task.id)},
        )
        await webhook_service.process_event(event)
    finally:
        ws_module.async_session_maker = original

    await db_session.refresh(task)
    assert task.status == TaskStatus.OVERDUE


@pytest.mark.asyncio
async def test_webhook_creates_audit_log(make_org, db_session):
    """A task_overdue event produces an audit log entry."""
    org = await make_org("Acme Corp")

    from app.models.task import Task, TaskPriority, TaskStatus as TS

    task = Task(
        organization_id=org.org_id,
        title="Audit target",
        status=TS.PENDING,
        priority=TaskPriority.LOW,
        created_by=org.admin_id,
    )
    db_session.add(task)
    await db_session.commit()

    import app.services.webhook_service as ws_module
    original = ws_module.async_session_maker
    ws_module.async_session_maker = org.session_maker

    try:
        from app.schemas.webhook import WebhookEvent
        await webhook_service.process_event(
            WebhookEvent(
                event_type="task_overdue",
                organization_id=org.org_id,
                payload={"task_id": str(task.id)},
            )
        )
    finally:
        ws_module.async_session_maker = original

    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.organization_id == org.org_id,
            AuditLog.action == "task_marked_overdue",
        )
    )
    log = result.scalar_one_or_none()
    assert log is not None
    assert log.entity_id == task.id


@pytest.mark.asyncio
async def test_webhook_respects_tenant(make_org, db_session):
    """An event for org_a must not affect org_b's tasks."""
    org_a = await make_org("Acme Corp")
    org_b = await make_org("Globex Inc")

    from app.models.task import Task, TaskPriority, TaskStatus as TS

    task_b = Task(
        organization_id=org_b.org_id,
        title="Globex task",
        status=TS.PENDING,
        priority=TaskPriority.MEDIUM,
        created_by=org_b.admin_id,
    )
    db_session.add(task_b)
    await db_session.commit()

    import app.services.webhook_service as ws_module
    original = ws_module.async_session_maker
    ws_module.async_session_maker = org_a.session_maker

    try:
        from app.schemas.webhook import WebhookEvent
        # Send event for org_a but use task_b's ID — must not find it.
        await webhook_service.process_event(
            WebhookEvent(
                event_type="task_overdue",
                organization_id=org_a.org_id,
                payload={"task_id": str(task_b.id)},
            )
        )
    finally:
        ws_module.async_session_maker = original

    await db_session.refresh(task_b)
    # task_b must remain untouched.
    assert task_b.status == TS.PENDING
