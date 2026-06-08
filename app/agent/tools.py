"""
AI Agent Tools (Pillar 2 - Tool Calling)
==========================================
This file defines the tools (functions) the PydanticAI agent can invoke.

You should implement here:
- create_task_tool: Extracts task entities from the user's message,
  validates them using Pydantic schemas (TaskCreate), and inserts
  the task into the database via TaskService
- (Optional) list_tasks_tool: Retrieves tasks for the user's organization
- (Optional) update_task_tool: Modifies an existing task

Each tool must:
1. Accept typed parameters (validated by Pydantic)
2. Access the database session (passed via agent context/dependencies)
3. Respect multi-tenant isolation (use organization_id from context)
4. Return a structured result

Example:
    @agent.tool
    async def create_task(ctx, title: str, priority: str, department: str) -> dict:
        task = await task_service.create_task(ctx.db, ctx.org_id, TaskCreate(...))
        return {"task_id": str(task.id), "status": "created"}
"""
