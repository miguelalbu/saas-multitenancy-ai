"""
Task Service (Business Logic)
==============================
This file contains the business logic for task operations.

You should implement here:
- create_task(db, org_id, task_data): Creates a task in the database,
  scoped to the given organization
- get_tasks(db, org_id, filters): Lists tasks with organization filtering
- update_task(db, org_id, task_id, data): Updates a task
- mark_task_overdue(db, org_id, task_id): Changes status to overdue
  (used by webhook background tasks)

This service is called by:
- Task CRUD endpoints (app/api/v1/endpoints/tasks.py)
- AI Agent tools (app/agent/tools.py)
- Webhook background actions (app/services/webhook_service.py)
"""
