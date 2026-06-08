"""Authentication schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT claims used to build the authenticated request context."""

    sub: uuid.UUID
    organization_id: uuid.UUID
    scopes: list[str] = Field(default_factory=list)
    exp: int
