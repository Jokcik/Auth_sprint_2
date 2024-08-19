import os
from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles')

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

include(
    'components/database.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/auth_password_validation.py',
)

# Добавьте эти строки в конец файла

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

AUTH_API_LOGIN_URL = 'http://0.0.0.0:8001/api/v1/auth/login'  # Замените на реальный URL вашего Auth-сервиса
AUTH_API_GET_USER_URL = 'http://0.0.0.0:8001/api/v1/auth/me'  # Замените на реальный URL вашего Auth-сервиса

LANGUAGE_CODE = 'ru-RU'

LOCALE_PATHS = ['movies/locale']

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080",]

CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000",]
