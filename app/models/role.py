"""Role model (Pillar 1 - RBAC).

A Role bundles a set of permission scopes (e.g. ``task:read``). Roles are
tenant-scoped: each organization owns its own roles. A user's role scopes are
embedded into the JWT at login and checked by the permission dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Role(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_role_org_name"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )

    organization: Mapped[Organization] = relationship(back_populates="roles")
    users: Mapped[list[User]] = relationship(back_populates="role")
