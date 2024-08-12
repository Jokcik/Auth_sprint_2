import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_register(make_post_request, user_data):
    response, body = await make_post_request("/api/v1/auth/register", user_data)
    assert response.status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body


async def test_login(make_post_request, user_data):
    # First, register the user
    await make_post_request("/api/v1/auth/register", user_data)

    # Now, try to login
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response, body = await make_post_request("/api/v1/auth/login", login_data)
    assert response.status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body


async def test_logout(make_post_request, user_data):
    # Register and login to get token
    response, body = await make_post_request("/api/v1/auth/register", user_data)
    token = body["access_token"]

    # Logout
    headers = {"Authorization": f"Bearer {token}"}
    response, body = await make_post_request("/api/v1/auth/logout", headers=headers)
    assert response.status == HTTPStatus.OK
    assert body == {"detail": "Successfully logged out"}


async def test_refresh_token(make_post_request, user_data):
    # Register to get tokens
    response, body = await make_post_request("/api/v1/auth/register", user_data)
    refresh_token = body["refresh_token"]

    # Refresh token
    response, body = await make_post_request("/api/v1/auth/refresh", data={"refresh_token": refresh_token})
    assert response.status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body


async def test_me(make_get_request, make_post_request, user_data):
    # Register to get token
    response, body = await make_post_request("/api/v1/auth/register", user_data)
    token = body["access_token"]

    # Get user info
    headers = {"Authorization": f"Bearer {token}"}
    response, body = await make_get_request("/api/v1/auth/me", headers=headers)
    assert response.status == HTTPStatus.OK
    assert body["username"] == user_data["username"]
    assert body["email"] == user_data["email"]