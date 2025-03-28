from contextvars import ContextVar

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from core.logger import LOGGING
from logging import config

config.dictConfig(LOGGING)
request_id_ctx = ContextVar("request_id")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    project_name: str = "Auth Service"

    # Database settings
    database_url: str = Field(..., alias="DATABASE_URL")
    database_autocommit: bool = Field(..., alias="DATABASE_AUTOCOMMIT")
    database_autoflush: bool = Field(..., alias="DATABASE_AUTOCOMMIT")

    # JWT settings
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    enable_limiters: bool = Field(True, alias="ENABLE_LIMITERS")

    enable_tracing: bool = Field(True, alias="ENABLE_TRACING")
    jeager_agent_host: str = Field("localhost", alias="JEAGER_AGENT_HOST")
    jeager_agent_port: int = Field(6831, alias="JEAGER_AGENT_PORT")

    # Redis settings
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    # CORS settings
    cors_origins: list = ["*"]

    # Superuser creation
    first_superuser_email: str = Field(..., alias="FIRST_SUPERUSER_EMAIL")
    first_superuser_password: str = Field(..., alias="FIRST_SUPERUSER_PASSWORD")

    yandex_client_id: str = Field(..., alias="YANDEX_CLIENT_ID")
    yandex_client_secret: str = Field(..., alias="YANDEX_CLIENT_SECRET")

    vk_client_id: str = Field(..., alias="VK_CLIENT_ID")
    vk_client_secret: str = Field(..., alias="VK_CLIENT_SECRET")

    google_client_id: str = Field(..., alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., alias="GOOGLE_CLIENT_SECRET")


settings = Settings()
