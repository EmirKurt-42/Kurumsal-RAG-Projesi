"""Async engine and session management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from order_service.infrastructure.database.models import Base


class Database:
    """Owns the engine and hands out transactional, request-scoped sessions."""

    def __init__(self, url: str, *, echo: bool = False) -> None:
        self._engine: AsyncEngine = create_async_engine(url, echo=echo)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        """Create missing tables on startup.

        Good enough for a teaching template; real projects version their
        schema with migrations (Alembic) instead.
        """
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """Release the connection pool on shutdown."""
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield a session whose transaction spans one unit of work."""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
