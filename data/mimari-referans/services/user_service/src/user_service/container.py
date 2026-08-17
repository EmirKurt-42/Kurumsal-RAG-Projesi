"""Composition root: where abstractions meet implementations.

Together with ``api/dependencies.py`` this is the only module allowed to
instantiate infrastructure classes. The rest of the codebase talks to
interfaces and never learns which concrete technology it is running on.
"""

from user_service.infrastructure.config import Settings
from user_service.infrastructure.database.session import Database


class Container:
    """Holds the long-lived resources of one application instance.

    Created in ``main.create_app`` and stored on ``app.state``. Tests build
    their own container around a throwaway database — same wiring, different
    configuration.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.database_url, echo=settings.debug)

    async def startup(self) -> None:
        await self.database.create_schema()

    async def shutdown(self) -> None:
        await self.database.dispose()
