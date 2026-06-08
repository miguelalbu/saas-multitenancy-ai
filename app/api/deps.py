"""
Shared Dependencies (Dependency Injection)
==========================================
This file contains FastAPI dependencies used across all routes.

You should implement here:
- get_db(): AsyncGenerator that yields an AsyncSession from SQLAlchemy
- get_current_user(): Extracts and validates the JWT token from the request,
  returns the authenticated user
- get_current_organization(): Extracts the organization_id from the JWT token
  or from the X-Organization-ID header, ensuring multi-tenant isolation

Example:
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            yield session
"""
