from fastapi import status
from fastapi.testclient import TestClient

from src.features.users.schemas import UserCredentials


def test_create_user(user_credentials: UserCredentials, client: TestClient):
    response = client.post("/api/v1/users", json=user_credentials.model_dump())
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "password" not in response_body
