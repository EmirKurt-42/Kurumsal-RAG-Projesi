"""Presentation layer: HTTP endpoints, request/response schemas, error mapping.

Translates HTTP into application-layer calls and back. Contains no
business logic — a route that grows an ``if`` about business state is a
sign that logic belongs in a use case or the domain.
"""
