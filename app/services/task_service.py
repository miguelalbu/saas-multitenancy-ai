"""Task business logic.

Called by the CRUD endpoints (Pillar 1), the AI agent tools (Pillar 2) and the
webhook background actions (Pillar 3). All operations are organization-scoped.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.repositories import task_repository
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(
    db: AsyncSession,
    organization_id: uuid.UUID,
    data: TaskCreate,
    *,
    created_by: uuid.UUID | None = None,
) -> Task:
    task = Task(
        organization_id=organization_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        department=data.department,
        created_by=created_by,
    )
    task = await task_repository.create(db, task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(
    db: AsyncSession,
    organization_id: uuid.UUID,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Task], int]:
    return await task_repository.get_all(
        db, organization_id, skip=skip, limit=limit
    )


async def get_task(
    db: AsyncSession, organization_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    return await task_repository.get_by_id(db, organization_id, task_id)


async def update_task(
    db: AsyncSession,
    organization_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
) -> Task | None:
    task = await task_repository.get_by_id(db, organization_id, task_id)
    if task is None:
        return None
    changes = data.model_dump(exclude_unset=True)
    task = await task_repository.update(db, task, changes)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession, organization_id: uuid.UUID, task_id: uuid.UUID
) -> bool:
    task = await task_repository.get_by_id(db, organization_id, task_id)
    if task is None:
        return False
    await task_repository.delete(db, task)
    await db.commit()
    return True


async def mark_task_overdue(
    db: AsyncSession, organization_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    """Set a task's status to ``overdue`` (used by webhook background tasks)."""
    task = await task_repository.get_by_id(db, organization_id, task_id)
    if task is None:
        return None
    task = await task_repository.update(
        db, task, {"status": TaskStatus.OVERDUE}
    )
    await db.commit()
    await db.refresh(task)
    return task
