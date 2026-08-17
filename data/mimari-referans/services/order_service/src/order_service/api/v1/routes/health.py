"""Liveness endpoint for orchestrators and load balancers."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report that the process is up and serving requests."""
    return {"status": "ok", "service": "order-service"}
