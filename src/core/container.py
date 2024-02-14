from aiohttp import ClientSession
from dependency_injector import containers, providers
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..features.email.services import EmailHunterService
from .config import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.database.session",
        ],
        packages=[
            "src.features.users",
            "src.api.v1.endpoints",
        ],
    )

    settings = providers.ThreadSafeSingleton(Settings)

    db_engine = providers.ThreadSafeSingleton(
        create_async_engine,
        settings.provided.DB_URL,
    )
    db_session_factory = providers.ThreadSafeSingleton(
        async_sessionmaker,
        db_engine.provided,
    )

    email_validation_service_client = providers.Factory(
        ClientSession,
        base_url=settings.provided.EMAIL_HUNTER_URL,
    )
    email_validation_service = providers.Factory(
        EmailHunterService,
        email_validation_service_client,
        settings.provided.EMAIL_HUNTER_API_KEY,
    )

    passlib_context = providers.Object(CryptContext(schemes=["bcrypt"]))
