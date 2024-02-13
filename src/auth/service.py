from ..core.config import access_token_backend, refresh_token_backend
from ..features.users.models import User
from .schemas import JwtTokenPair, TokenSubject


def issue_tokens(user: User) -> JwtTokenPair:
    token_subject = TokenSubject(user_id=user.id)
    serialized_subject = token_subject.model_dump()
    token_pair = JwtTokenPair(
        access_token=access_token_backend.create_access_token(serialized_subject),
        refresh_token=refresh_token_backend.create_refresh_token(serialized_subject),
    )
    return token_pair
