"""Task data-access layer.

Every query is filtered by ``organization_id`` so a tenant can never read or
mutate another tenant's tasks.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


async def get_by_id(
    db: AsyncSession, organization_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def get_all(
    db: AsyncSession,
    organization_id: uuid.UUID,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Task], int]:
    base = select(Task).where(Task.organization_id == organization_id)

    total = await db.scalar(
        select(func.count()).select_from(base.subquery())
    )
    result = await db.execute(
        base.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), int(total or 0)


async def create(db: AsyncSession, task: Task) -> Task:
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def update(db: AsyncSession, task: Task, data: dict) -> Task:
    for field, value in data.items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return task


async def delete(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.flush()
