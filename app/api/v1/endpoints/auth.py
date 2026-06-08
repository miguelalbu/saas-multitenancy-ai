"""
Authentication Endpoints
========================
This file handles user authentication and token generation.

You should implement here:
- POST /login: Accepts credentials, validates against the database,
  returns a JWT access token containing user_id and organization_id
- (Optional) POST /register: Creates a new user within an organization

The JWT token must include:
- sub: user ID
- organization_id: the tenant scope
- scopes: list of permissions (e.g., ["task:read", "task:write"])

Use the security utilities from app.core.security for password hashing
and token encoding/decoding.
"""
