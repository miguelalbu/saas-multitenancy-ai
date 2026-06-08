"""Authentication endpoints (Pillar 1)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import create_access_token, verify_password
from app.repositories import user_repository
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
    x_organization_id: uuid.UUID | None = Header(default=None),
) -> TokenResponse:
    """Validate credentials and issue a JWT carrying tenant + scopes.

    Because email is only unique *within* an organization, an optional
    ``X-Organization-ID`` header can disambiguate the tenant. When omitted, the
    first active user matching the email is used.
    """
    if x_organization_id is not None:
        user = await user_repository.get_by_email(
            db, x_organization_id, payload.email
        )
    else:
        user = await user_repository.get_by_email_global(db, payload.email)

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )

    token = create_access_token(
        user_id=user.id,
        organization_id=user.organization_id,
        scopes=user.role.scopes,
    )
    return TokenResponse(access_token=token)
