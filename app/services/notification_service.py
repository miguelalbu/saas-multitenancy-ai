"""Notification service — bridges background tasks with WebSocket push (Pillar 3)."""

from __future__ import annotations

import uuid

from app.core.websocket_manager import manager
from app.schemas.websocket import WSNotification


async def notify(org_id: uuid.UUID, notification_type: str, data: dict) -> None:
    """Push a structured notification to all WebSocket clients of ``org_id``."""
    msg = WSNotification(type=notification_type, data=data)
    await manager.broadcast(org_id, msg.model_dump(mode="json"))
