"""
User Model (Pillar 1 - Auth & RBAC)
=====================================
This file defines the User SQLAlchemy model.

You should implement here:
- User class inheriting from Base
- Fields: id (UUID), email (str, unique within org), hashed_password (str),
  organization_id (FK to organizations), role_id (FK to roles),
  is_active (bool), created_at (datetime)
- Relationships: organization, role

The user is always scoped to an organization. Authentication returns
a JWT containing the user's organization_id and role scopes.
"""
