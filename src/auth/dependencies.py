from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi_jwt import JwtAuthorizationCredentials

from ..core.config import access_token_backend, refresh_token_backend
from ..features.users.exceptions import InvalidCredentials, UserNotFound
from ..features.users.models import User
from ..features.users.schemas import UserCredentials
from ..features.users.services import UsersService
from .schemas import JwtTokenPair, TokenSubject
from .service import issue_tokens


def validate_access_token(
    token_payload: JwtAuthorizationCredentials = Security(access_token_backend),
) -> TokenSubject:
    return TokenSubject.model_validate(token_payload.subject)


async def get_user(
    token_subject: Annotated[TokenSubject, Depends(validate_access_token)],
    users_service: Annotated[UsersService, Depends()],
) -> User:
    user = await users_service.get_user_by_id(token_subject.user_id)
    return user


async def refresh_token(
    users_service: Annotated[UsersService, Depends()],
    token_payload: JwtAuthorizationCredentials = Security(refresh_token_backend),
) -> JwtTokenPair:
    subject = TokenSubject.model_validate(token_payload.subject)
    user = await users_service.get_user_by_id(subject.user_id)
    return issue_tokens(user)


async def authenticate_user(
    credentials: UserCredentials,
    users_service: Annotated[UsersService, Depends()],
) -> JwtTokenPair:
    try:
        user = await users_service.get_user_by_credentials(credentials)
    except (UserNotFound, InvalidCredentials) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid credentials") from exc
    return issue_tokens(user)


AuthenticationRequired = Depends(validate_access_token)
CurrentUser = Annotated[User, Depends(get_user)]
