"""Task CRUD endpoints (Pillar 1).

Every route requires authentication, is automatically scoped to the caller's
organization, and is gated by an RBAC scope.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core import scopes
from app.core.permissions import require_scope
from app.schemas.task import TaskCreate, TaskList, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter()


@router.get("", response_model=TaskList)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current: CurrentUser = Depends(require_scope(scopes.TASK_READ)),
    db: AsyncSession = Depends(get_db),
) -> TaskList:
    items, total = await task_service.get_tasks(
        db, current.organization_id, skip=skip, limit=limit
    )
    return TaskList(
        items=[TaskResponse.model_validate(t) for t in items], total=total
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current: CurrentUser = Depends(require_scope(scopes.TASK_WRITE)),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await task_service.create_task(
        db, current.organization_id, payload, created_by=current.user.id
    )
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current: CurrentUser = Depends(require_scope(scopes.TASK_READ)),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await task_service.get_task(db, current.organization_id, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current: CurrentUser = Depends(require_scope(scopes.TASK_WRITE)),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await task_service.update_task(
        db, current.organization_id, task_id, payload
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current: CurrentUser = Depends(require_scope(scopes.TASK_DELETE)),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await task_service.delete_task(
        db, current.organization_id, task_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
