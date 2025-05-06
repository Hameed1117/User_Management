import pytest
from httpx import AsyncClient
from app.services.user_service import UserService
from app.main import app


@pytest.mark.asyncio
async def test_create_user_internal_failure(mocker, async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_data = {
        "nickname": "newuser",
        "email": "new_user@example.com",
        "password": "NewUserStrong#Pass123",
        "first_name": "John",
        "last_name": "Doe",
        "role": "AUTHENTICATED"
    }

    mocker.patch.object(UserService, "get_by_email", return_value=None)
    mocker.patch.object(UserService, "create", return_value=None)

    response = await async_client.post("/users/", json=user_data, headers=headers)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create user"


@pytest.mark.asyncio
async def test_update_user_not_found(mocker, async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = "00000000-0000-0000-0000-000000000999"
    mocker.patch.object(UserService, "update", return_value=None)

    response = await async_client.put(f"/users/{fake_id}", json={"email": "newemail@example.com"}, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_user_not_found(mocker, async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    mocker.patch.object(UserService, "get_by_id", return_value=None)

    response = await async_client.get(f"/users/00000000-0000-0000-0000-000000000999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_register_user_success(mocker, async_client):
    mock_user = {
        "id": "e3c6d212-d511-4f75-b5c3-b1777d730a00",
        "nickname": "newuser",
        "first_name": "New",
        "last_name": "User",
        "bio": "Test bio",
        "role": "AUTHENTICATED",
        "email": "newuser@example.com",
        "profile_picture_url": None,
        "github_profile_url": None,
        "linkedin_profile_url": None,
        "last_login_at": None,
        "created_at": "2024-05-05T00:00:00Z",
        "updated_at": "2024-05-05T00:00:00Z",
        "links": {}
    }

    mocker.patch.object(UserService, "register_user", return_value=mock_user)

    response = await async_client.post("/register/", json={
        "nickname": mock_user["nickname"],
        "email": mock_user["email"],
        "password": "StrongPassword!123",
        "first_name": mock_user["first_name"],
        "last_name": mock_user["last_name"],
        "role": mock_user["role"]
    })

    assert response.status_code == 200
    assert response.json()["email"] == mock_user["email"]


@pytest.mark.asyncio
async def test_list_users_empty(mocker, async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    mocker.patch.object(UserService, "count", return_value=0)
    mocker.patch.object(UserService, "list_users", return_value=[])

    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
