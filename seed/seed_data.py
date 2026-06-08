"""
Seed Data Script
=================
This file populates the database with minimal test data.

You should implement here:
- Create at least 2 Organizations (to test multi-tenant isolation)
- Create users with different roles/scopes in each organization
- Create sample tasks in each organization
- Create roles with different permission sets

Run with: python -m seed.seed_data

Example seed data:
- Org 1: "Acme Corp" with admin user + regular user
- Org 2: "Globex Inc" with admin user + regular user
- Tasks in each org (should NOT be visible cross-org)
- Roles: "admin" (all scopes), "member" (task:read only)

Make sure to handle the async database session properly
(use asyncio.run() as the entry point).
"""
