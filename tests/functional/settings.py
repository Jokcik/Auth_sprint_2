from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    db_name: str = Field(..., alias='POSTGRES_DB')
    db_user: str = Field(..., alias='POSTGRES_USER')
    db_password: str = Field(..., alias='POSTGRES_PASSWORD')
    db_host: str = Field('localhost', alias='POSTGRES_HOST')
    db_port: int = Field(5432, alias='POSTGRES_PORT')

    redis_host: str = Field('127.0.0.1', description='Хост Redis сервера', alias='REDIS_HOST')
    redis_port: int = Field(6379, description='Порт Redis сервера', alias='REDIS_PORT')

    service_url: str = Field('http://localhost:8000', alias='SERVICE_URL')


test_settings = TestSettings()
