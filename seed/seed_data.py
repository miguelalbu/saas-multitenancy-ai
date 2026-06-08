"""Seed script: minimal multi-tenant test data.

Creates two isolated organizations (Acme Corp and Globex Inc), each with an
``admin`` role (all scopes) and a ``member`` role (read-only), two users and a
couple of tasks. Running it again is a no-op (idempotent on organization name).

Run with: ``python -m seed.seed_data``
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import async_session_maker, dispose_engine
from app.core.scopes import ALL_SCOPES, MEMBER_SCOPES
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.role import Role
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

DEFAULT_PASSWORD = "password123"


async def _seed_organization(
    session,
    *,
    org_name: str,
    admin_email: str,
    member_email: str,
    task_titles: list[str],
) -> None:
    existing = await session.scalar(
        select(Organization).where(Organization.name == org_name)
    )
    if existing is not None:
        print(f"  - '{org_name}' already exists, skipping")
        return

    org = Organization(name=org_name)
    session.add(org)
    await session.flush()

    admin_role = Role(
        organization_id=org.id, name="admin", scopes=list(ALL_SCOPES)
    )
    member_role = Role(
        organization_id=org.id, name="member", scopes=list(MEMBER_SCOPES)
    )
    session.add_all([admin_role, member_role])
    await session.flush()

    admin = User(
        organization_id=org.id,
        email=admin_email,
        hashed_password=hash_password(DEFAULT_PASSWORD),
        role_id=admin_role.id,
    )
    member = User(
        organization_id=org.id,
        email=member_email,
        hashed_password=hash_password(DEFAULT_PASSWORD),
        role_id=member_role.id,
    )
    session.add_all([admin, member])
    await session.flush()

    for title in task_titles:
        session.add(
            Task(
                organization_id=org.id,
                title=title,
                description=f"Seed task for {org_name}",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                department="General",
                created_by=admin.id,
            )
        )

    print(f"  - created '{org_name}' (admin={admin_email}, member={member_email})")


async def seed() -> None:
    print("Seeding database...")
    async with async_session_maker() as session:
        await _seed_organization(
            session,
            org_name="Acme Corp",
            admin_email="admin@acme.com",
            member_email="member@acme.com",
            task_titles=["Prepare Q3 roadmap", "Review onboarding flow"],
        )
        await _seed_organization(
            session,
            org_name="Globex Inc",
            admin_email="admin@globex.com",
            member_email="member@globex.com",
            task_titles=["Audit security policy", "Plan offsite event"],
        )
        await session.commit()

    print(f"Done. Default password for every seeded user: '{DEFAULT_PASSWORD}'")
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(seed())
