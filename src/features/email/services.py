from typing import Protocol

from aiohttp import ClientSession
from fastapi import status

from .constants import EmailHunterForbiddenStatuses
from .exceptions import EmailValidationRequestFailed
from .models import EmailHunterRequestParams, EmailHunterResponse


class EmailValidationService(Protocol):
    async def email_is_valid(self, email: str) -> bool: ...


class EmailHunterService:
    def __init__(self, client: ClientSession, api_key: str) -> None:
        self._client = client
        self._api_key = api_key

    async def email_is_valid(self, email: str) -> bool:
        result = await self._check_email(email)
        return result not in EmailHunterForbiddenStatuses

    async def _check_email(self, email: str) -> EmailHunterResponse:
        request_params = EmailHunterRequestParams(
            email=email,
            api_key=self._api_key,
        )
        async with self._client.get(
            "/v2/email-verifier",
            params=request_params,
        ) as response:
            if response.status != status.HTTP_200_OK:
                raise EmailValidationRequestFailed()
            response_body = await response.json()
            return EmailHunterResponse.model_validate(response_body.get("data"))
