from collections.abc import Sequence
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select

from src.database.session import Session

from ..users.models import User
from .exceptions import (
    InvalidReferral,
    ReferralCodeAlreadyExists,
    ReferralCodeExpired,
    ReferralCodeNotFound,
)
from .models import ReferralCode


class ReferralsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_code_by_id(self, code_id: UUID) -> ReferralCode:
        referral_code = await self.session.get(ReferralCode, code_id)
        if not referral_code:
            raise ReferralCodeNotFound()
        return referral_code

    async def get_active_code_by_email(self, email: str) -> ReferralCode:
        active_referral = await self.session.scalar(
            select(ReferralCode).where(
                ReferralCode.owner.has(User.email == email),
                ReferralCode.expiration_date >= date.today(),
            )
        )
        if not active_referral:
            raise ReferralCodeNotFound()
        return active_referral

    async def create_code(
        self,
        owner: User,
        expiration_date: date,
    ) -> ReferralCode:
        existing_active_referral = await self.session.scalar(
            select(ReferralCode).where(
                ReferralCode.owner == owner,
                ReferralCode.expiration_date >= date.today(),
            )
        )
        if existing_active_referral:
            raise ReferralCodeAlreadyExists()
        referral_code = ReferralCode(
            id=uuid4(),
            expiration_date=expiration_date,
        )
        referral_code.owner = owner
        self.session.add(referral_code)
        await self.session.flush()
        await self.session.refresh(referral_code)
        return referral_code

    async def delete_code(self, referral_code: ReferralCode) -> None:
        await self.session.delete(referral_code)
        await self.session.flush()

    async def get_referees(self, referrer_id: int) -> Sequence[User]:
        referees = (
            await self.session.scalars(
                select(User).where(
                    User.registration_referral.has(ReferralCode.owner_id == referrer_id)
                )
            )
        ).all()
        return referees

    async def add_referee(self, referral_code: ReferralCode, user: User) -> None:
        if not self.referral_is_active(referral_code):
            raise ReferralCodeExpired()
        if referral_code.owner is user:
            raise InvalidReferral()
        user.registration_referral = referral_code
        self.session.add(user)
        await self.session.flush()

    def referral_is_active(self, referral_code: ReferralCode) -> bool:
        return referral_code.expiration_date >= date.today()
