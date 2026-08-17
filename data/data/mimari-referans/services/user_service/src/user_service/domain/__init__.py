"""Domain layer: pure business rules.

This package must not import anything from outside itself — no FastAPI,
no SQLAlchemy, not even Pydantic. If a framework import ever appears here,
the architecture has been violated.
"""
