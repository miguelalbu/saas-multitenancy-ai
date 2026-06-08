"""Webhook event processing service (Pillar 3).

Events received at POST /v1/webhook/event are dispatched here as background
tasks. Each handler:
  1. Performs a database action (update status, write audit log).
  2. Pushes a WebSocket notification to all connected clients of the org.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.audit_log import AuditLog
from app.schemas.webhook import WebhookEvent
from app.services import notification_service, task_service


async def _write_audit_log(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None,
    details: dict,
) -> AuditLog:
    log = AuditLog(
        organization_id=org_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)
    await db.flush()
    return log


async def _handle_task_overdue(org_id: uuid.UUID, payload: dict) -> None:
    """Mark a task as overdue and emit a WebSocket notification."""
    task_id_raw = payload.get("task_id")
    if not task_id_raw:
        return

    task_id = uuid.UUID(str(task_id_raw))

    async with async_session_maker() as db:
        task = await task_service.mark_task_overdue(db, org_id, task_id)
        if task is None:
            return

        await _write_audit_log(
            db,
            org_id=org_id,
            action="task_marked_overdue",
            entity_type="task",
            entity_id=task.id,
            details={"title": task.title, "trigger": "webhook"},
        )
        await db.commit()

    await notification_service.notify(
        org_id,
        "task_updated",
        {"task_id": str(task_id), "status": "overdue", "title": task.title},
    )


async def _handle_financial_alert(org_id: uuid.UUID, payload: dict) -> None:
    """Log a financial alert and notify connected clients."""
    async with async_session_maker() as db:
        await _write_audit_log(
            db,
            org_id=org_id,
            action="financial_alert_received",
            entity_type="system",
            entity_id=None,
            details=payload,
        )
        await db.commit()

    await notification_service.notify(
        org_id,
        "financial_alert",
        {"message": payload.get("message", "Financial alert received"), **payload},
    )


_HANDLERS = {
    "task_overdue": _handle_task_overdue,
    "financial_alert": _handle_financial_alert,
}


async def process_event(event: WebhookEvent) -> None:
    """Dispatch a webhook event to the appropriate async handler.

    Unknown event types are logged as generic audit entries so no data is lost.
    """
    handler = _HANDLERS.get(event.event_type)
    if handler:
        await handler(event.organization_id, event.payload)
    else:
        # Persist unknown events as audit logs for traceability.
        async with async_session_maker() as db:
            await _write_audit_log(
                db,
                org_id=event.organization_id,
                action=f"unknown_event:{event.event_type}",
                entity_type="system",
                entity_id=None,
                details=event.payload,
            )
            await db.commit()

        await notification_service.notify(
            event.organization_id,
            "system_event",
            {"event_type": event.event_type, **event.payload},
        )
