from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from src.features.users.schemas import UserCredentials, UserOut
from src.features.users.services import UsersService

router = APIRouter(tags=["users"])


@router.get("/me")
async def get_current_user() -> UserOut: ...


@router.post("", response_model=UserOut)
async def create_user(
    credentials: UserCredentials,
    users_service: Annotated[UsersService, Depends()],
) -> Any:
    user = await users_service.create_user(credentials)
    await users_service.session.commit()
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_user(
    user_id: int,
    users_service: Annotated[UsersService, Depends()],
) -> None: ...
