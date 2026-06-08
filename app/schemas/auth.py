"""
Authentication Schemas
=======================
Pydantic models for authentication request/response validation.

You should implement here:
- LoginRequest: email (EmailStr), password (str)
- TokenResponse: access_token (str), token_type (str = "bearer")
- TokenPayload: sub (str/UUID), organization_id (str/UUID),
  scopes (list[str]), exp (datetime)
"""
