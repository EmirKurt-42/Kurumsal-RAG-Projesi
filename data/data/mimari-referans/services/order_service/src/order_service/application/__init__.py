"""Application layer: use cases and the ports they depend on.

May import ``domain`` only. Declares the interfaces (ports) it needs from
the outside world — including the other microservice, hidden behind
``UserGateway`` — and never touches their implementations.
"""
