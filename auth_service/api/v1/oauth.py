from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from services.oauth_service import oauth
from services.user_service import UserService
from db.database import get_db

router = APIRouter()

@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    oauth_provider = oauth.create_client(provider)
    redirect_uri = request.url_for('auth_callback', provider=provider)
    return await oauth_provider.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback/{provider}")
async def auth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    oauth_provider = oauth.create_client(provider)
    token = await oauth_provider.authorize_access_token(request)
    user_info = await oauth_provider.parse_id_token(request, token)

    # Проверка существующего пользователя или создание нового
    user_service = UserService(db)
    user = user_service.get_or_create_user_oauth(provider, user_info)

    # Логика авторизации (например, установка сессии)
    response = RedirectResponse(url="/")
    response.set_cookie("user_id", user.id)
    return response