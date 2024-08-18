from authlib.integrations.starlette_client import OAuth
from core.config import settings

oauth = OAuth()

# Регистрация OAuth провайдеров
oauth.register(
    name='yandex',
    client_id=settings.YANDEX_CLIENT_ID,
    client_secret=settings.YANDEX_CLIENT_SECRET,
    authorize_url='https://oauth.yandex.ru/authorize',
    access_token_url='https://oauth.yandex.ru/token',
    client_kwargs={'scope': 'login:email login:info'}
)

oauth.register(
    name='vk',
    client_id=settings.VK_CLIENT_ID,
    client_secret=settings.VK_CLIENT_SECRET,
    authorize_url='https://oauth.vk.com/authorize',
    access_token_url='https://oauth.vk.com/access_token',
    client_kwargs={'scope': 'email'}
)

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid email profile'}
)