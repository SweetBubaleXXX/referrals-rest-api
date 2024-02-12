import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.users.exceptions import (
    InvalidCredentials,
    UserAlreadyExists,
    UserNotFound,
)
from src.features.users.models import User
from src.features.users.schemas import UserCredentials
from src.features.users.services import UsersService


@pytest.mark.asyncio
async def test_get_user_by_id(users_service: UsersService, saved_user: User):
    found_user = await users_service.get_user_by_id(saved_user.id)
    assert found_user is saved_user


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(users_service: UsersService):
    with pytest.raises(UserNotFound):
        await users_service.get_user_by_id(123)


@pytest.mark.asyncio
async def test_get_user_by_credentials(
    users_service: UsersService,
    user_credentials: UserCredentials,
):
    await users_service.create_user(user_credentials)
    found_user = await users_service.get_user_by_credentials(user_credentials)
    assert found_user.email == user_credentials.email


@pytest.mark.asyncio
async def test_get_user_by_credentials_invalid_password(
    users_service: UsersService,
    user_credentials: UserCredentials,
):
    await users_service.create_user(user_credentials)
    user_credentials.password = "invalid_password"
    with pytest.raises(InvalidCredentials):
        await users_service.get_user_by_credentials(user_credentials)


@pytest.mark.asyncio
async def test_create_user(
    users_service: UsersService,
    user_credentials: UserCredentials,
    db_session: AsyncSession,
):
    created_user = await users_service.create_user(user_credentials)
    assert user_credentials.password != created_user.password
    (
        await db_session.scalars(
            select(User).where(User.email == user_credentials.email)
        )
    ).one()


@pytest.mark.asyncio
async def test_create_user_already_exists(
    users_service: UsersService,
    saved_user,
    user_credentials: UserCredentials,
):
    with pytest.raises(UserAlreadyExists):
        await users_service.create_user(user_credentials)


@pytest.mark.asyncio
async def test_delete_user(
    users_service: UsersService,
    saved_user: User,
    db_session: AsyncSession,
):
    await users_service.delete_user(saved_user.id)
    user_in_db = await db_session.scalar(
        select(User).where(User.email == saved_user.email)
    )
    assert not user_in_db
