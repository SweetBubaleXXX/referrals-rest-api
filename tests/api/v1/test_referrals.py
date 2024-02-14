from datetime import date
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Settings
from src.features.referrals.models import ReferralCode
from src.features.referrals.schemas import ReferralCodeIn
from src.features.users.models import User
from tests.factories import UserFactory


def test_get_code_by_email(
    saved_user: User,
    saved_referral: ReferralCode,
    client: TestClient,
    settings: Settings,
):
    response = client.get(
        f"{settings.API_V1_PREFIX}/referrals/codes",
        params={"referrer_email": saved_user.email},
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["id"] == str(saved_referral.id)


def test_get_code_by_email_not_found(client: TestClient, settings: Settings):
    response = client.get(
        f"{settings.API_V1_PREFIX}/referrals/codes",
        params={"referrer_email": "test@mail.com"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_code(
    saved_user: User,
    client: TestClient,
    settings: Settings,
    tomorrow: date,
):
    request = ReferralCodeIn(expiration_date=tomorrow)

    response = client.post(
        f"{settings.API_V1_PREFIX}/referrals/codes",
        json=request.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert response_body["owner_id"] == saved_user.id


def test_create_code_already_exists(
    saved_referral: ReferralCode,
    client: TestClient,
    settings: Settings,
    tomorrow: date,
):
    request = ReferralCodeIn(expiration_date=tomorrow)

    response = client.post(
        f"{settings.API_V1_PREFIX}/referrals/codes",
        json=request.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_code_past_date(
    client: TestClient,
    settings: Settings,
    yesterday: date,
):
    request = ReferralCodeIn.model_construct(expiration_date=yesterday)

    response = client.post(
        f"{settings.API_V1_PREFIX}/referrals/codes",
        json=request.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_code(
    saved_referral: ReferralCode,
    client: TestClient,
    settings: Settings,
):
    response = client.delete(
        f"{settings.API_V1_PREFIX}/referrals/codes/{saved_referral.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_code_not_found(
    client: TestClient,
    settings: Settings,
):
    nonexistent_id = uuid4()

    response = client.delete(
        f"{settings.API_V1_PREFIX}/referrals/codes/{nonexistent_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_code_of_another_user(
    db_session: AsyncSession,
    client: TestClient,
    settings: Settings,
    tomorrow: date,
):
    foreign_code_id = uuid4()
    foreign_code = ReferralCode(id=foreign_code_id, expiration_date=tomorrow)
    another_user: User = UserFactory()  # type: ignore
    foreign_code.owner = another_user
    db_session.add(foreign_code)
    await db_session.commit()

    response = client.delete(
        f"{settings.API_V1_PREFIX}/referrals/codes/{foreign_code_id}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
