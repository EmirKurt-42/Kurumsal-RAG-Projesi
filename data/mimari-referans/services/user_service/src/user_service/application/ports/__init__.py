"""Ports: interfaces the application layer requires from the outside world.

Dependency Inversion in practice — the *inner* layer owns the contract,
the *outer* layer (infrastructure) supplies an adapter that fulfils it.
"""

from user_service.application.ports.user_repository import UserRepository

__all__ = ["UserRepository"]
