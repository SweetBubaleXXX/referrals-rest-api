from typing import Literal, TypedDict

from pydantic import BaseModel

EmailHunterResponseStatus = Literal[
    "valid",
    "invalid",
    "accept_all",
    "webmail",
    "disposable",
    "unknown",
]


class EmailHunterRequestParams(TypedDict):
    email: str
    api_key: str


class EmailHunterResponse(BaseModel):
    status: EmailHunterResponseStatus
