"""WebSocket notification schemas (Pillar 3)."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class WSNotification(BaseModel):
    type: str
    data: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
