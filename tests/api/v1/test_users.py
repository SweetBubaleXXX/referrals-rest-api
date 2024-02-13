from fastapi import status
from fastapi.testclient import TestClient

from src.features.users.models import User
from src.features.users.schemas import UserCredentials


def test_create_user(client: TestClient):
    credentials = UserCredentials(email="test@mail.com", password="password")
    response = client.post("/api/v1/users", json=credentials.model_dump())
    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    assert "password" not in response_body


def test_delete_user(saved_user: User, client: TestClient):
    response = client.delete(f"/api/v1/users/{saved_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_another_user(client: TestClient):
    response = client.delete("/api/v1/users/123")
    assert response.status_code == status.HTTP_403_FORBIDDEN
