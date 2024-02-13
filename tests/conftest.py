from datetime import date, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src import main
from src.auth.schemas import TokenSubject
from src.core.config import Settings, access_token_backend
from src.core.container import Container
from src.database.models import Base
from src.database.session import get_session
from src.features.referrals.models import ReferralCode
from src.features.referrals.services import ReferralsService
from src.features.users.models import User
from src.features.users.schemas import UserCredentials
from src.features.users.services import UsersService

from .factories import UserFactory


@pytest.fixture(scope="session")
def container():
    return main.container


@pytest.fixture(scope="session")
def settings(container: Container):
    return container.settings()


@pytest.fixture(scope="session", autouse=True)
def override_db_engine(container: Container, settings: Settings):
    engine = create_async_engine(settings.TEST_DB_URL, poolclass=NullPool)
    with container.db_engine.override(engine):
        yield


@pytest_asyncio.fixture(autouse=True)
async def setup_database(container: Container):
    engine = container.db_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(container: Container):
    session_generator = get_session(container.db_session_factory())
    async with await anext(session_generator) as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def trigger_lifespan_events(app: FastAPI):
    async with LifespanManager(app):
        yield


@pytest.fixture
def users_service(db_session: AsyncSession):
    return UsersService(db_session)


@pytest.fixture
def user():
    return UserFactory()


@pytest_asyncio.fixture
async def saved_user(user: User, db_session: AsyncSession):
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_credentials(user):
    return UserCredentials.model_validate(user, from_attributes=True)


@pytest.fixture
def auth_headers(saved_user: User):
    access_token = access_token_backend.create_access_token(
        TokenSubject(user_id=saved_user.id).model_dump()
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def tomorrow():
    return date.today() + timedelta(days=1)


@pytest.fixture
def referral_code(tomorrow: date):
    return ReferralCode(id=uuid4(), expiration_date=tomorrow)


@pytest_asyncio.fixture
async def saved_referral(
    referral_code: ReferralCode,
    saved_user: User,
    db_session: AsyncSession,
):
    referral_code.owner = saved_user
    db_session.add(referral_code)
    await db_session.commit()
    await db_session.refresh(referral_code)
    await db_session.refresh(saved_user)
    return referral_code


@pytest.fixture
def referrals_service(db_session: AsyncSession):
    return ReferralsService(db_session)


@pytest.fixture(scope="session")
def app():
    app = main.create_app()
    return app


@pytest.fixture
def client(auth_headers: dict, app: FastAPI):
    with TestClient(app, headers=auth_headers) as client:
        yield client
