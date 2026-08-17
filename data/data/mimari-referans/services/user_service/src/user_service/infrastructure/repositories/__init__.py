"""Adapters implementing the application layer's repository ports."""

from user_service.infrastructure.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)

__all__ = ["SqlAlchemyUserRepository"]
