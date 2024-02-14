from datetime import date

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.features.referrals.models import ReferralCode
from src.features.users.models import User
from src.features.users.schemas import UserCredentials
from tests.factories import UserFactory


@pytest.mark.asyncio
async def test_get_referees(
    saved_referral: ReferralCode,
    saved_user: User,
    db_session: AsyncSession,
    client: TestClient,
    settings: Settings,
):
    referrer_id = saved_user.id
    referees = [UserFactory() for _ in range(5)]
    (await saved_referral.awaitable_attrs.referees).extend(referees)
    db_session.add(saved_referral)
    await db_session.commit()

    response = client.get(f"{settings.API_V1_PREFIX}/users/{referrer_id}/referees")
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 5


def test_get_referees_empty(saved_user: User, client: TestClient, settings: Settings):
    response = client.get(f"{settings.API_V1_PREFIX}/users/{saved_user.id}/referees")
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert len(response_body) == 0


def test_create_user(client: TestClient, settings: Settings):
    credentials = UserCredentials(email="test@mail.com", password="password")

    response = client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={"credentials": credentials.model_dump()},
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "password" not in response_body


@pytest.mark.asyncio
async def test_create_user_with_referral(
    saved_referral: ReferralCode,
    db_session: AsyncSession,
    client: TestClient,
    settings: Settings,
):
    credentials = UserCredentials(email="test@mail.com", password="password")

    response = client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "credentials": credentials.model_dump(),
            "referral_code": str(saved_referral.id),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    user_id = response.json()["id"]
    user_in_db = await db_session.get_one(User, user_id)
    assert await user_in_db.awaitable_attrs.registration_referral is saved_referral


@pytest.mark.asyncio
async def test_create_user_with_expired_referral(
    yesterday: date,
    saved_referral: ReferralCode,
    db_session: AsyncSession,
    client: TestClient,
    settings: Settings,
):
    referral_id = saved_referral.id
    saved_referral.expiration_date = yesterday
    db_session.add(saved_referral)
    await db_session.commit()
    credentials = UserCredentials(email="test@mail.com", password="password")

    response = client.post(
        f"{settings.API_V1_PREFIX}/users",
        json={
            "credentials": credentials.model_dump(),
            "referral_code": str(referral_id),
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_user(saved_user: User, client: TestClient, settings: Settings):
    response = client.delete(f"{settings.API_V1_PREFIX}/users/{saved_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_another_user(client: TestClient, settings: Settings):
    response = client.delete(f"{settings.API_V1_PREFIX}/users/123")
    assert response.status_code == status.HTTP_403_FORBIDDEN
