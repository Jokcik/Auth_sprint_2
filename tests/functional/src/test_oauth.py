from http import HTTPStatus
import pytest
from models.user import User

@pytest.mark.asyncio
async def test_oauth_login_redirect(make_get_request):
    response, _ = await make_get_request("/api/v1/oauth/login/google")
    assert response.status_code == HTTPStatus.FOUND
    assert "accounts.google.com" in response.headers["location"]

@pytest.mark.asyncio
async def test_oauth_callback_creates_user(make_get_request, make_post_request, db):
    token = {"access_token": "fake-access-token"}
    user_info = {
        "sub": "123456789",
        "email": "oauthuser@example.com",
        "name": "OAuth User"
    }

    response, _ = await make_get_request("/api/v1/oauth/auth/callback/google?code=fake-code")
    assert response.status_code == HTTPStatus.FOUND

    user = db.query(User).filter_by(email=user_info["email"]).first()
    assert user is not None
    assert user.oauth_provider == "google"
    assert user.oauth_id == user_info["sub"]

@pytest.mark.asyncio
async def test_oauth_callback_existing_user(make_get_request, create_oauth_user, db):
    response, _ = await make_get_request("/api/v1/oauth/auth/callback/google?code=fake-code")
    assert response.status_code == HTTPStatus.FOUND

    user = db.query(User).filter_by(email="oauthuser@example.com").first()
    assert user is not None
    assert user.id == create_oauth_user.id