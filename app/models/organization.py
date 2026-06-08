"""Organization model (Pillar 1 - Multi-Tenant).

An Organization is a tenant. All tenant-scoped rows reference it through
``organization_id`` to guarantee strict data isolation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.task import Task
    from app.models.user import User


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list[User]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    roles: Mapped[list[Role]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    tasks: Mapped[list[Task]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
