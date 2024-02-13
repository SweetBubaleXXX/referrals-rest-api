from fastapi import FastAPI

from .api.v1.router import v1_router
from .core.container import Container
from .core.exceptions import setup_exception_handlers

container = Container()


def create_app() -> FastAPI:
    settings = container.settings()

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )

    setup_exception_handlers(app)

    app.include_router(v1_router, prefix=settings.API_V1_STR)

    return app
