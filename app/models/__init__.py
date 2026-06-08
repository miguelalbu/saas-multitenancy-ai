"""Model registry.

Importing every model here ensures they are registered on ``Base.metadata``
so Alembic autogenerate can detect all tables.
"""

from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

__all__ = [
    "Base",
    "Organization",
    "Role",
    "User",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "AuditLog",
]
