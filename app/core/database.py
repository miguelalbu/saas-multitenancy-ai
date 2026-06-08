"""
Database Configuration
=======================
This file sets up the async SQLAlchemy engine and session factory.

You should implement here:
- Create an AsyncEngine using create_async_engine() with the DATABASE_URL
  from settings
- Create an async_session_maker using sessionmaker() with class_=AsyncSession
- (Optional) A helper function to initialize/close the engine on app startup/shutdown

Example:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

This session factory is used by the get_db() dependency in app/api/deps.py.
"""
