"""Infrastructure layer: adapters for the application's ports.

Everything technology-specific lives here — the database engine, ORM
models, repository implementations and runtime configuration. This layer
imports the inner layers; they never import it back.
"""
