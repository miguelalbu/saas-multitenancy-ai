"""AI agent tools (Pillar 2 - Tool Calling).

Each tool is a typed async function decorated with ``@agent.tool``. PydanticAI
validates the arguments extracted by the LLM against the type annotations and
passes the request context (DB session + org id) through ``RunContext``.

Tools are registered on the agent in ``app/agent/agent.py``.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from pydantic_ai import RunContext

from app.core.database import async_session_maker
from app.schemas.task import TaskCreate
from app.services import task_service


@dataclass
class AgentDeps:
    """Dependencies injected into every tool call via RunContext.

    Tools open their own sessions rather than sharing the request session.
    ``session_factory`` is injected so tests can substitute the test engine
    without touching global state.
    """

    organization_id: uuid.UUID
    user_id: uuid.UUID
    session_factory: object = None  # async_sessionmaker; defaults to prod factory

    def get_session(self):
        factory = self.session_factory or async_session_maker
        return factory()


async def create_task(
    ctx: RunContext[AgentDeps],
    title: str,
    priority: str = "medium",
    department: str | None = None,
    description: str | None = None,
) -> dict:
    """Create a new task in the user's organization.

    Args:
        title: Concise task name extracted from the user's message.
        priority: One of low, medium, high, urgent.
        department: Business unit responsible for the task.
        description: Optional extra details.

    Returns:
        A dict with task_id, title and status confirming the creation.
    """
    data = TaskCreate(
        title=title,
        priority=priority,  # type: ignore[arg-type]  Pydantic coerces the str
        department=department,
        description=description,
    )
    async with ctx.deps.get_session() as db:
        task = await task_service.create_task(
            db,
            ctx.deps.organization_id,
            data,
            created_by=ctx.deps.user_id,
        )
    return {
        "task_id": str(task.id),
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
        "department": task.department,
    }


async def list_tasks(
    ctx: RunContext[AgentDeps],
    limit: int = 10,
) -> dict:
    """List the most recent tasks in the user's organization.

    Args:
        limit: Maximum number of tasks to return (default 10, max 50).

    Returns:
        A dict with a ``tasks`` list and ``total`` count.
    """
    limit = min(limit, 50)
    async with ctx.deps.get_session() as db:
        items, total = await task_service.get_tasks(
            db, ctx.deps.organization_id, limit=limit
        )
    return {
        "total": total,
        "tasks": [
            {
                "task_id": str(t.id),
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value,
                "department": t.department,
            }
            for t in items
        ],
    }
