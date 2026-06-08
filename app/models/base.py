"""SQLAlchemy declarative base with multi-tenant mixin."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
