from authlib.integrations.starlette_client import OAuth
from core.config import settings

oauth = OAuth()

# Регистрация OAuth провайдеров
oauth.register(
    name='yandex',
    client_id=settings.yandex_client_id,
    client_secret=settings.yandex_client_secret,
    authorize_url='https://oauth.yandex.ru/authorize',
    access_token_url='https://oauth.yandex.ru/token',
    client_kwargs={'scope': 'login:email login:info'}
)

oauth.register(
    name='vk',
    client_id=settings.vk_client_id,
    client_secret=settings.vk_client_secret,
    authorize_url='https://oauth.vk.com/authorize',
    access_token_url='https://oauth.vk.com/access_token',
    client_kwargs={'scope': 'email'}
)

oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid email profile'}
)