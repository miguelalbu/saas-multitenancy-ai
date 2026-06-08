"""
Task CRUD Tests
================
Test the task endpoints with RBAC and multi-tenant isolation.

You should implement here:
- test_create_task: Authenticated user can create a task
- test_list_tasks: Returns only tasks from the user's organization
- test_get_task_not_found: 404 for non-existent or cross-org task
- test_create_task_forbidden: User without "task:write" scope gets 403
- test_list_tasks_requires_permission: User without "task:read" gets 403
"""
