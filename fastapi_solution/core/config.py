from functools import lru_cache
from logging import config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

config.dictConfig(LOGGING)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


class ProjectConfig(BaseConfig):
    project_name: str = Field('movies', description='Имя проекта', alias='PROJECT_NAME')
    cache_expire: int = Field(1, description='Время жизни кэша в секундах', alias='REDIS_EXPIRE')

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"

    es_film_index: str = Field('movies', description='Индекс Elasticsearch для фильмов', alias='ELASTIC_MOVIE_INDEX')
    es_person_index: str = Field('persons', description='Индекс Elasticsearch для персон', alias='ELASTIC_PERSON_INDEX')
    es_genre_index: str = Field('genres', description='Индекс Elasticsearch для жанров', alias='ELASTIC_GENRE_INDEX')

    def __hash__(self):
        return hash(self.project_name)


class RedisConfig(BaseConfig):
    host: str = Field('127.0.0.1', description='Хост Redis сервера', alias='REDIS_HOST')
    port: int = Field(6379, description='Порт Redis сервера', alias='REDIS_PORT')


class ElasticConfig(BaseConfig):
    host: str = Field('http://127.0.0.1', description='Хост сервера Elasticsearch', alias='ELASTIC_HOST')
    port: int = Field(9200, description='Порт сервера Elasticsearch', alias='ELASTIC_PORT')


@lru_cache()
def get_project_config() -> ProjectConfig:
    return ProjectConfig()
