"""Runtime configuration, loaded from environment variables and ``.env``.

Pydantic is acceptable in this layer: configuration is an infrastructure
concern, and settings never travel into the domain.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings (prefix: ``USER_SERVICE_``)."""

    model_config = SettingsConfigDict(
        env_prefix="USER_SERVICE_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "user-service"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./users.db"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (read once, then cached)."""
    return Settings()
