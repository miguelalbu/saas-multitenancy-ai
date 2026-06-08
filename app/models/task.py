"""
Task Model (Core Business Entity)
===================================
This file defines the Task SQLAlchemy model.

You should implement here:
- Task class inheriting from Base
- Fields: id (UUID), title (str), description (str, optional),
  status (enum: pending/in_progress/completed/overdue),
  priority (enum: low/medium/high/urgent),
  department (str), organization_id (FK to organizations),
  created_by (FK to users), created_at (datetime), updated_at (datetime)
- Relationships: organization, creator (user)

This is the main entity manipulated by:
- The AI Agent (Pillar 2) via tool calling
- The webhook automation engine (Pillar 3) for status changes
- CRUD endpoints with RBAC protection (Pillar 1)
"""
