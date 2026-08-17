"""Adapter: SQLAlchemy implementation of the ``UserRepository`` port."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.application.ports.user_repository import UserRepository
from user_service.domain.entities.user import User
from user_service.domain.value_objects.email import Email
from user_service.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    """Persists ``User`` entities in a relational database.

    This class is the only place where the domain and the ORM meet: it
    translates ``User`` (entity) ↔ ``UserModel`` (row) in both directions.
    SQL stops here and never leaks into the layers above.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(self._to_row(user))
        await self._session.flush()

    async def get(self, user_id: UUID) -> User | None:
        row = await self._session.get(UserModel, str(user_id))
        return self._to_entity(row) if row is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        statement = select(UserModel).where(UserModel.email == str(email))
        row = (await self._session.execute(statement)).scalar_one_or_none()
        return self._to_entity(row) if row is not None else None

    async def list_all(self) -> list[User]:
        statement = select(UserModel).order_by(UserModel.created_at.desc())
        rows = (await self._session.execute(statement)).scalars().all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_row(user: User) -> UserModel:
        return UserModel(
            id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    @staticmethod
    def _to_entity(row: UserModel) -> User:
        # SQLite discards timezone info; normalise back to UTC on the way out.
        created_at = (
            row.created_at if row.created_at.tzinfo else row.created_at.replace(tzinfo=UTC)
        )
        return User(
            id=UUID(row.id),
            email=Email(row.email),
            full_name=row.full_name,
            is_active=row.is_active,
            created_at=created_at,
        )
