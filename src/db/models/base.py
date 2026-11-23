"""Declarative base and shared metadata for cigarlog ORM models."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base.

    All ORM-mapped classes inherit from this. The ``metadata`` attribute on
    this class is what Alembic uses for autogenerate comparison.
    """
    pass
