"""
Security Utilities (Pillar 1)
==============================
This file provides JWT and password hashing utilities.

You should implement here:
- create_access_token(data: dict) -> str: Encodes a JWT with user_id,
  organization_id, scopes, and expiration
- verify_token(token: str) -> TokenPayload: Decodes and validates a JWT,
  raising HTTPException 401 if invalid/expired
- hash_password(password: str) -> str: Hashes a plain-text password using bcrypt
- verify_password(plain: str, hashed: str) -> bool: Verifies a password

Use PyJWT for token operations and passlib[bcrypt] for passwords.
Settings (secret key, algorithm, expiration) come from app.config.settings.
"""
