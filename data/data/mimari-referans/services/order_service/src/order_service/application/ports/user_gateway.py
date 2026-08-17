"""Port: the order service's view of the user service.

An *anti-corruption layer* in miniature: instead of importing another
service's client (or worse, its database), this service defines the tiny
interface it actually needs. How the answer is obtained — HTTP, gRPC, a
cache, a test fake — is an infrastructure detail.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class UserGateway(ABC):
    """Read-only questions this service may ask about users."""

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """Return ``True`` if the user exists and is active.

        Implementations raise ``UserServiceUnavailableError`` when the
        answer cannot be obtained at all.
        """
