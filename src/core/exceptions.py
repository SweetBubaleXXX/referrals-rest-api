from fastapi import FastAPI, HTTPException, Request, status

from src.features.users.exceptions import UserAlreadyExists, UserNotFound


def not_found_handler(request: Request, exc: BaseException):
    message = str(exc) or "Resource not found"
    raise HTTPException(status.HTTP_404_NOT_FOUND, message) from exc


def already_exists_handler(request: Request, exc: BaseException):
    message = str(exc) or "Already exists"
    raise HTTPException(status.HTTP_400_BAD_REQUEST, message) from exc


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFound, not_found_handler)
    app.add_exception_handler(UserAlreadyExists, already_exists_handler)
