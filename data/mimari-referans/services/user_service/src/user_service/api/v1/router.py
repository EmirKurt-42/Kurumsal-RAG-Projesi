"""Aggregates every v1 route under a single, versioned router."""

from fastapi import APIRouter

from user_service.api.v1.routes import health, users

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(users.router)
