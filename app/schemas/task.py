"""
Task Schemas
=============
Pydantic models for task CRUD and AI agent tool validation.

You should implement here:
- TaskCreate: title (str), description (str, optional),
  priority (enum: low/medium/high/urgent), department (str)
- TaskUpdate: partial fields for PATCH/PUT
- TaskResponse: all fields + id, status, created_at, updated_at
- TaskList: list of TaskResponse with pagination metadata

These schemas are also used by the PydanticAI agent tools
to validate extracted entities before inserting into the database.
"""
