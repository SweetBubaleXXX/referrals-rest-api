import secrets
from datetime import timedelta

from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from pydantic_settings import BaseSettings, SettingsConfigDict

MODEL_CONFIG = SettingsConfigDict(
    env_file=(".env", ".env.prod"),
    extra="ignore",
)


class Settings(BaseSettings):
    API_TITLE: str = "API"
    API_DESCRIPTION: str = ""
    API_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api"

    DB_URL: str = "sqlite+aiosqlite:///:memory:"
    TEST_DB_URL: str = "sqlite+aiosqlite:///:memory:"

    model_config = MODEL_CONFIG


class AuthSettings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)

    model_config = MODEL_CONFIG


auth_settings = AuthSettings()

access_token_backend = JwtAccessBearer(
    secret_key=auth_settings.SECRET_KEY,
    access_expires_delta=timedelta(hours=1),
    refresh_expires_delta=timedelta(days=7),
)
refresh_token_backend: JwtRefreshBearer = JwtRefreshBearer.from_other(
    access_token_backend,
)  # type: ignore
