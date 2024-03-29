from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, status

from src.auth.dependencies import CurrentUser
from src.core.container import Container
from src.features.email.services import EmailValidationService
from src.features.referrals.services import ReferralsService
from src.features.users.schemas import UserCredentials, UserOut
from src.features.users.services import UsersService

router = APIRouter(tags=["users"])


@router.get("/{user_id}/referees", response_model=list[UserOut])
async def get_referees(
    user_id: int,
    referrals_service: Annotated[ReferralsService, Depends()],
):
    return await referrals_service.get_referees(user_id)


@router.post("")
@inject
async def create_user(
    credentials: UserCredentials,
    users_service: Annotated[UsersService, Depends()],
    referrals_service: Annotated[ReferralsService, Depends()],
    referral_code: Annotated[UUID | None, Body()] = None,
    email_validation_service: EmailValidationService = Depends(
        Provide[Container.email_validation_service]
    ),
) -> UserOut:
    if not await email_validation_service.email_is_valid(credentials.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid email address")
    user = await users_service.create_user(credentials)
    if referral_code:
        await referrals_service.add_referee(referral_code, user)
    user_response = UserOut.model_validate(user)
    await users_service.session.commit()
    return user_response


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    users_service: Annotated[UsersService, Depends()],
) -> None:
    if user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    await users_service.delete_user(current_user)
    await users_service.session.commit()
