"""Adapters implementing the application layer's gateway ports."""

from order_service.infrastructure.gateways.http_user_gateway import HttpUserGateway

__all__ = ["HttpUserGateway"]
