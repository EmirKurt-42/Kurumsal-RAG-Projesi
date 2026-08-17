"""HTTP endpoints for user management.

Thin by design: validate the wire format, call a use case, shape the
response. Each handler body is three steps — anything longer probably
belongs in the application layer.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from user_service.api.dependencies import get_get_user, get_list_users, get_register_user
from user_service.api.v1.schemas.user import RegisterUserRequest, UserResponse
from user_service.application.dto import RegisterUserInput
from user_service.application.use_cases.get_user import GetUser
from user_service.application.use_cases.list_users import ListUsers
from user_service.application.use_cases.register_user import RegisterUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterUserRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
) -> UserResponse:
    """Register a new user."""
    output = await use_case.execute(
        RegisterUserInput(email=payload.email, full_name=payload.full_name)
    )
    return UserResponse.model_validate(output)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    use_case: Annotated[GetUser, Depends(get_get_user)],
) -> UserResponse:
    """Fetch a single user by id."""
    return UserResponse.model_validate(await use_case.execute(user_id))


@router.get("", response_model=list[UserResponse])
async def list_users(
    use_case: Annotated[ListUsers, Depends(get_list_users)],
) -> list[UserResponse]:
    """List all users, newest first."""
    return [UserResponse.model_validate(user) for user in await use_case.execute()]
