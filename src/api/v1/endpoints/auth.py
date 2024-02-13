from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.dependencies import authenticate_user, refresh_token
from src.auth.schemas import JwtTokenPair

router = APIRouter(tags=["auth"])


@router.post("/jwt/access")
def create_jwt_token_pair(
    token_pair: Annotated[JwtTokenPair, Depends(authenticate_user)],
) -> JwtTokenPair:
    return token_pair


@router.post("/jwt/refresh")
def refresh_jwt_token(
    token_pair: Annotated[JwtTokenPair, Depends(refresh_token)],
) -> JwtTokenPair:
    return token_pair
