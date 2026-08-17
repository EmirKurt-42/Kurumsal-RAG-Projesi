"""Ports: interfaces the application layer requires from the outside world.

Note that ``UserGateway`` makes *another microservice* a pluggable detail,
exactly like the database: the use case cannot tell HTTP from a test fake.
"""

from order_service.application.ports.order_repository import OrderRepository
from order_service.application.ports.user_gateway import UserGateway

__all__ = ["OrderRepository", "UserGateway"]
