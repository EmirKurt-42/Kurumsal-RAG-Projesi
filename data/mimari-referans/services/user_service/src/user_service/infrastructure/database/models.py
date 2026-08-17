"""SQLAlchemy ORM models — the persistence shape of the domain.

Deliberately separate from domain entities: the table layout may evolve
(indexes, denormalisation, column renames) without touching business code.
The repository adapter is the only place that translates between the two.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models of this service."""


class UserModel(Base):
    """Row shape of the ``users`` table."""

    __tablename__ = "users"

    # UUIDs are stored as their 36-char text form for SQLite compatibility.
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
