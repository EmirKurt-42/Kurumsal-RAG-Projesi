"""FastAPI dependency wiring — request-scoped assembly of use cases.

``Depends`` is our delivery mechanism for dependency injection: each
request gets a fresh session, a repository bound to it and a fully built
use case. Routes only ever declare *what* they need; the choice of
concrete classes is made here and in ``container.py``.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.application.ports.user_repository import UserRepository
from user_service.application.use_cases.get_user import GetUser
from user_service.application.use_cases.list_users import ListUsers
from user_service.application.use_cases.register_user import RegisterUser
from user_service.container import Container
from user_service.infrastructure.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def get_container(request: Request) -> Container:
    """Fetch the application-wide container created in ``main.create_app``."""
    container: Container = request.app.state.container
    return container


async def get_session(
    container: Annotated[Container, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped session: commits on success, rolls back on error."""
    async with container.database.session() as session:
        yield session


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Bind the ``UserRepository`` port to its SQLAlchemy adapter."""
    return SqlAlchemyUserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_register_user(users: UserRepositoryDep) -> RegisterUser:
    return RegisterUser(users)


def get_get_user(users: UserRepositoryDep) -> GetUser:
    return GetUser(users)


def get_list_users(users: UserRepositoryDep) -> ListUsers:
    return ListUsers(users)
