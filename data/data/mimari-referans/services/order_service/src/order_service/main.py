"""Application entry point — the app factory.

Run locally with:

    uvicorn order_service.main:app --reload --port 8002

Creating orders requires user_service to be reachable (default:
http://localhost:8001 — see infrastructure/config.py).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from order_service.api.exception_handlers import register_exception_handlers
from order_service.api.v1.router import router as v1_router
from order_service.container import Container
from order_service.infrastructure.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Tie the container's resources to the application's life cycle."""
    container: Container = app.state.container
    await container.startup()
    yield
    await container.shutdown()


def create_app(container: Container | None = None) -> FastAPI:
    """Build a fully wired application instance.

    The optional ``container`` parameter is the test seam: integration
    tests pass a container configured with a throwaway in-memory database
    and get an otherwise identical application.
    """
    app = FastAPI(
        title="Order Service",
        version="1.0.0",
        description="Manages orders; verifies buyers against the user service. "
        "A Clean Architecture reference implementation.",
        lifespan=lifespan,
    )
    app.state.container = container or Container(get_settings())

    app.include_router(v1_router)
    register_exception_handlers(app)
    return app


app = create_app()
