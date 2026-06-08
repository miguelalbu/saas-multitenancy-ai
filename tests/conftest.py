"""Shared pytest fixtures.

Tests run against a dedicated ``desafio_test`` database so they never touch
development/seed data. The schema is created fresh (drop+create) for every
test function to guarantee full isolation.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.models  # noqa: F401  -- registers all models on Base.metadata
from app.api.deps import get_db
from app.config import settings
from app.core.scopes import ALL_SCOPES, MEMBER_SCOPES
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User

TEST_DB_NAME = "desafio_test"
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DB_NAME}"
)


async def _ensure_test_database() -> None:
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def engine():
    """Function-scoped engine: drops and recreates the schema for each test."""
    await _ensure_test_database()
    _engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture
async def test_session_maker(engine):
    """Expose the test async_sessionmaker so agent tools can use the test DB."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(test_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine, test_session_maker, db_session) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with get_db overridden to the test database."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


class OrgFixture:
    def __init__(
        self,
        org_id: uuid.UUID,
        admin_id: uuid.UUID,
        member_id: uuid.UUID,
        admin_headers: dict[str, str],
        member_headers: dict[str, str],
        session_maker,
    ) -> None:
        self.org_id = org_id
        self.admin_id = admin_id
        self.member_id = member_id
        self.admin_headers = admin_headers
        self.member_headers = member_headers
        self.session_maker = session_maker  # passed to AgentDeps in chat tests


@pytest_asyncio.fixture
async def make_org(db_session, test_session_maker):
    """Factory that creates an organization with an admin + member user."""

    async def _make(name: str) -> OrgFixture:
        org = Organization(name=name)
        db_session.add(org)
        await db_session.flush()

        admin_role = Role(
            organization_id=org.id, name="admin", scopes=list(ALL_SCOPES)
        )
        member_role = Role(
            organization_id=org.id, name="member", scopes=list(MEMBER_SCOPES)
        )
        db_session.add_all([admin_role, member_role])
        await db_session.flush()

        slug = name.lower().replace(" ", "")
        admin = User(
            organization_id=org.id,
            email=f"admin@{slug}.com",
            hashed_password=hash_password("password123"),
            role_id=admin_role.id,
        )
        member = User(
            organization_id=org.id,
            email=f"member@{slug}.com",
            hashed_password=hash_password("password123"),
            role_id=member_role.id,
        )
        db_session.add_all([admin, member])
        await db_session.commit()

        def headers(user_id, scopes):
            token = create_access_token(
                user_id=user_id, organization_id=org.id, scopes=scopes
            )
            return {"Authorization": f"Bearer {token}"}

        return OrgFixture(
            org_id=org.id,
            admin_id=admin.id,
            member_id=member.id,
            admin_headers=headers(admin.id, ALL_SCOPES),
            member_headers=headers(member.id, MEMBER_SCOPES),
            session_maker=test_session_maker,
        )

    return _make
