"""Audit log model (Pillar 3 - Event Tracking).

Audit logs record significant state changes. They are written by webhook
background tasks and by AI agent tool calls. ``performed_by`` is nullable so
that system-generated actions (e.g. an automated status change) can be logged
without a user.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin


class AuditLog(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
