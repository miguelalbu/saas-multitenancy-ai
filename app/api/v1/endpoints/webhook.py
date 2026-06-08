"""Webhook/trigger endpoint (Pillar 3).

Receives external events, validates the payload and fires the processing logic
as a background task so the HTTP response returns immediately (202 Accepted).
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.deps import CurrentUser
from app.core import scopes
from app.core.permissions import require_scope
from app.schemas.webhook import WebhookEvent, WebhookResponse
from app.services import webhook_service

router = APIRouter()


@router.post(
    "/event",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def receive_event(
    event: WebhookEvent,
    background_tasks: BackgroundTasks,
    current: CurrentUser = Depends(require_scope(scopes.WEBHOOK_MANAGE)),
) -> WebhookResponse:
    """Accept an external event and dispatch async processing.

    The event is validated by Pydantic, then handed off to a background task
    (``asyncio.create_task``) so the response is returned immediately. The
    background task updates the database and pushes a WebSocket notification
    to all connected clients of the organization.
    """
    # Force the event to be scoped to the authenticated org (security guard).
    scoped_event = WebhookEvent(
        event_type=event.event_type,
        organization_id=current.organization_id,
        payload=event.payload,
    )

    asyncio.create_task(webhook_service.process_event(scoped_event))

    return WebhookResponse(
        status="accepted",
        message=f"Event '{event.event_type}' queued for processing.",
    )
