"""
Organization Model (Pillar 1 - Multi-Tenant)
==============================================
This file defines the Organization SQLAlchemy model.

You should implement here:
- Organization class inheriting from Base
- Fields: id (UUID, primary key), name (str), created_at (datetime)
- Relationships: users, tasks (one-to-many)

This model represents a tenant in the multi-tenant architecture.
All tenant-scoped models must have a foreign key to this table.
"""
