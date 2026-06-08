"""Webhook event schemas (Pillar 3)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    event_type: str
    organization_id: uuid.UUID
    payload: dict = {}


class WebhookResponse(BaseModel):
    status: str
    message: str
