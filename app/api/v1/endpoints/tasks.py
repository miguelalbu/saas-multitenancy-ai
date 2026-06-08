"""
Task CRUD Endpoints
====================
This file implements CRUD operations for tasks.

You should implement here:
- GET /v1/tasks: List all tasks (filtered by organization_id automatically)
- POST /v1/tasks: Create a new task
- GET /v1/tasks/{id}: Get a single task by ID
- PUT /v1/tasks/{id}: Update a task
- DELETE /v1/tasks/{id}: Delete a task

All routes must:
1. Require authentication (use get_current_user dependency)
2. Filter by organization_id (multi-tenant isolation)
3. Validate permissions via RBAC (e.g., require "task:read" or "task:write" scopes)
4. Use Pydantic schemas for request/response validation
"""
