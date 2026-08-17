"""Request/response schemas for the ``/users`` endpoints.

These Pydantic models are the *wire format* — they mirror, but are distinct
from, application DTOs and domain entities, so the public contract can
evolve independently of the inner layers.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RegisterUserRequest(BaseModel):
    """Payload for ``POST /users``.

    Only *shape* is validated here (types, lengths). Whether the e-mail is
    actually well-formed is a business rule and is enforced by the ``Email``
    value object in the domain — try registering ``"not-an-email"`` and
    watch where the error comes from.
    """

    email: str = Field(max_length=320, examples=["ada@example.com"])
    full_name: str = Field(min_length=1, max_length=200, examples=["Ada Lovelace"])


class UserResponse(BaseModel):
    """Public representation of a user."""

    # from_attributes lets FastAPI build this straight from a UserOutput DTO.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
