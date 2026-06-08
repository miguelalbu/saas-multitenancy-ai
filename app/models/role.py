"""
Role / Permission Model (Pillar 1 - RBAC)
===========================================
This file defines the Role and Permission models for access control.

You should implement here:
- Role class: id (UUID), name (str, e.g., "admin", "member"),
  organization_id (FK), scopes (list of permission strings)
- Store scopes as a JSON array or a separate permissions table

Example scopes: ["task:read", "task:write", "chat:use", "webhook:manage"]

The role's scopes are embedded in the JWT token at login and checked
by the permissions middleware on each protected route.
"""
