from pydantic import BaseModel


class TokenSubject(BaseModel):
    user_id: int


class JwtTokenPair(BaseModel):
    access_token: str
    refresh_token: str
