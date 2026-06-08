"""Shared FastAPI dependencies (database session, auth, tenant context)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user_repository

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass
class CurrentUser:
    """Authenticated request context resolved from the JWT.

    ``scopes`` come from the token (snapshot taken at login) and are used for
    RBAC checks. ``organization_id`` is the tenant boundary applied to every
    query.
    """

    user: User
    organization_id: uuid.UUID
    scopes: list[str]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session."""
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """Decode the JWT, load the user and build the tenant-scoped context."""
    payload = decode_access_token(credentials.credentials)

    user = await user_repository.get_by_id(db, payload.sub)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Defence in depth: the token's tenant must match the stored user's tenant.
    if user.organization_id != payload.organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token organization mismatch",
        )

    return CurrentUser(
        user=user,
        organization_id=payload.organization_id,
        scopes=payload.scopes,
    )


async def get_current_organization(
    current_user: CurrentUser = Depends(get_current_user),
) -> uuid.UUID:
    """Return the organization id that scopes the current request."""
    return current_user.organization_id
