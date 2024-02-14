from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

from src.auth.dependencies import CurrentUser
from src.features.referrals.schemas import ReferralCodeIn, ReferralCodeOut
from src.features.referrals.services import ReferralsService

router = APIRouter(tags=["referrals"])


@router.get("/codes", response_model=ReferralCodeOut)
async def get_code_by_email(
    referrer_email: EmailStr,
    referrals_service: Annotated[ReferralsService, Depends()],
):
    referral_code = await referrals_service.get_active_code_by_email(referrer_email)
    return referral_code


@router.post("/codes")
async def create_code(
    referral_code: ReferralCodeIn,
    current_user: CurrentUser,
    referrals_service: Annotated[ReferralsService, Depends()],
) -> ReferralCodeOut:
    created_code = await referrals_service.create_code(
        current_user,
        referral_code.expiration_date,
    )
    code_response = ReferralCodeOut.model_validate(created_code)
    await referrals_service.session.commit()
    return code_response


@router.delete("/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_code(
    code_id: UUID,
    current_user: CurrentUser,
    referrals_service: Annotated[ReferralsService, Depends()],
) -> None:
    referral_code = await referrals_service.get_code_by_id(code_id)
    if referral_code.owner_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not the owner of the referral code",
        )
    await referrals_service.delete_code(referral_code)
    await referrals_service.session.commit()
