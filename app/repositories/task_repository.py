"""
Task Repository (Data Access Layer)
=====================================
This file encapsulates all database queries for the Task model.

You should implement here:
- get_by_id(db, org_id, task_id): Fetch a single task (filtered by org)
- get_all(db, org_id, skip, limit): List tasks with pagination
- create(db, task: Task): Insert a new task
- update(db, task: Task, data: dict): Update task fields
- delete(db, task: Task): Remove a task

All queries MUST filter by organization_id to enforce multi-tenant isolation.
Never return data from another organization.

Example:
    async def get_all(db: AsyncSession, org_id: UUID, skip=0, limit=20):
        query = select(Task).where(Task.organization_id == org_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
"""
