"""User data-access layer."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(
    db: AsyncSession, organization_id: uuid.UUID, email: str
) -> User | None:
    """Fetch a user by email within a single organization."""
    result = await db.execute(
        select(User).where(
            User.organization_id == organization_id,
            User.email == email,
        )
    )
    return result.scalar_one_or_none()


async def get_by_email_global(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by email across organizations (first active match).

    Used at login when the tenant is not yet known from the request.
    """
    result = await db.execute(
        select(User).where(User.email == email, User.is_active.is_(True))
    )
    return result.scalars().first()


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Fetch a user by primary key."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user: User) -> User:
    """Persist a new user."""
    db.add(user)
    await db.flush()
    return user
