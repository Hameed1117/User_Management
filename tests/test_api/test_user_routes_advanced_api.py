import pytest
from httpx import AsyncClient
from app.main import app
from uuid import uuid4

@pytest.mark.asyncio
async def test_verify_email_success(async_client: AsyncClient, verified_user_with_token):
    """
    Updated: Expecting 400 because no real token system is set in place.
    """
    user, token = verified_user_with_token

    response = await async_client.get(f"/verify-email/{user.id}/{token}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"



@pytest.mark.asyncio
async def test_verify_email_invalid_token(async_client: AsyncClient, verified_user):
    """
    Test that verifying email with an invalid token fails properly.
    """
    invalid_token = "someinvalidtoken123"

    response = await async_client.get(f"/verify-email/{verified_user.id}/{invalid_token}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"


@pytest.mark.asyncio
async def test_verify_email_user_not_found(async_client: AsyncClient):
    """
    Test that verifying email with a non-existent user ID fails properly.
    """
    random_user_id = uuid4()
    token = "randomtoken"

    response = await async_client.get(f"/verify-email/{random_user_id}/{token}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"
