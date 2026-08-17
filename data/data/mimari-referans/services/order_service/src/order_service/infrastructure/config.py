"""Runtime configuration, loaded from environment variables and ``.env``."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings (prefix: ``ORDER_SERVICE_``)."""

    model_config = SettingsConfigDict(
        env_prefix="ORDER_SERVICE_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "order-service"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./orders.db"
    # Base URL of the user service; overridden in docker-compose.
    user_service_url: str = "http://localhost:8001"
    user_service_timeout_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (read once, then cached)."""
    return Settings()
