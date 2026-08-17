"""Order service — a Clean Architecture reference microservice.

Layer map (imports always point inwards):

    api  ──►  application  ──►  domain  ◄──  infrastructure

Compared to user_service this service adds a richer domain model (the
``Order`` aggregate, ``Money``) and cross-service communication behind a
port (``UserGateway``).
"""

__version__ = "1.0.0"
