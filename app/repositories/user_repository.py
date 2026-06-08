"""
User Repository (Data Access Layer)
=====================================
This file encapsulates all database queries for the User model.

You should implement here:
- get_by_email(db, org_id, email): Fetch a user by email within an org
- get_by_id(db, user_id): Fetch a user by ID
- create(db, user: User): Insert a new user

Used by authentication logic to validate credentials and by
the dependency injection system to resolve the current user.
"""
