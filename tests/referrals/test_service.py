from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.referrals.exceptions import (
    InvalidReferral,
    ReferralCodeAlreadyExists,
    ReferralCodeNotFound,
)
from src.features.referrals.models import ReferralCode
from src.features.referrals.services import ReferralsService
from src.features.users.models import User

from ..factories import UserFactory


@pytest.mark.asyncio
async def test_get_code_by_id(
    referrals_service: ReferralsService,
    saved_referral: ReferralCode,
):
    found_referral_code = await referrals_service.get_code_by_id(saved_referral.id)
    assert found_referral_code.expiration_date == saved_referral.expiration_date


@pytest.mark.asyncio
async def test_get_active_referral_by_email(
    referrals_service: ReferralsService,
    saved_referral: ReferralCode,
    saved_user: User,
):
    found_referral = await referrals_service.get_active_code_by_email(saved_user.email)
    assert found_referral is saved_referral


@pytest.mark.asyncio
async def test_create_code(
    referrals_service: ReferralsService,
    saved_user: User,
    db_session: AsyncSession,
    tomorrow: date,
):
    referral_code = await referrals_service.create_code(saved_user, tomorrow)
    code_in_db = await db_session.scalar(
        select(ReferralCode).where(ReferralCode.expiration_date == tomorrow)
    )
    assert code_in_db
    assert referral_code.owner_id is saved_user.id


@pytest.mark.asyncio
async def test_only_one_active_referral(
    referrals_service: ReferralsService,
    saved_user: User,
    tomorrow: date,
):
    await referrals_service.create_code(saved_user, tomorrow)
    with pytest.raises(ReferralCodeAlreadyExists):
        await referrals_service.create_code(saved_user, tomorrow)


@pytest.mark.asyncio
async def test_delete_code(
    saved_referral: ReferralCode,
    referrals_service: ReferralsService,
    db_session: AsyncSession,
):
    await referrals_service.delete_code(saved_referral)
    code_in_db = await db_session.get(ReferralCode, saved_referral.id)
    assert not code_in_db


@pytest.mark.asyncio
async def test_get_referees_empty(
    referrals_service: ReferralsService,
    saved_user: User,
):
    referees = await referrals_service.get_referees(saved_user.id)
    assert len(referees) == 0


@pytest.mark.asyncio
async def test_get_referees(
    referrals_service: ReferralsService,
    saved_referral: ReferralCode,
    saved_user: User,
    db_session: AsyncSession,
):
    referees = [UserFactory() for _ in range(5)]
    (await saved_referral.awaitable_attrs.referees).extend(referees)
    db_session.add(saved_referral)
    await db_session.flush()

    found_referees = await referrals_service.get_referees(saved_user.id)
    assert len(found_referees) == 5


@pytest.mark.asyncio
async def test_add_referee(
    referral_code: ReferralCode,
    referrals_service: ReferralsService,
    saved_user: User,
    db_session: AsyncSession,
):
    referral_owner: User = UserFactory()  # type: ignore
    referral_code.owner = referral_owner
    db_session.add(referral_code)
    await db_session.flush()

    await referrals_service.add_referee(referral_code.id, saved_user)
    assert saved_user in await referral_code.awaitable_attrs.referees


@pytest.mark.asyncio
async def test_add_referee_not_found(user: User, referrals_service: ReferralsService):
    with pytest.raises(ReferralCodeNotFound):
        await referrals_service.add_referee(uuid4(), user)


@pytest.mark.asyncio
async def test_add_referee_own_referral(
    referral_code: ReferralCode,
    referrals_service: ReferralsService,
    saved_user: User,
    db_session: AsyncSession,
):
    referral_code.owner = saved_user
    db_session.add(referral_code)
    await db_session.flush()

    with pytest.raises(InvalidReferral):
        await referrals_service.add_referee(referral_code.id, saved_user)
