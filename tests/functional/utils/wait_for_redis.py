import logging
import backoff

from pydantic import Field
from pydantic_settings import BaseSettings
from redis import Redis


class Settings(BaseSettings):
    redis_host: str = Field('localhost', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')


@backoff.on_exception(
    backoff.expo,
    exception=(Exception,),
    max_tries=8,
    factor=2,
)
def wait_for_redis():
    settings = Settings()
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    try:
        redis_client.ping()
        logging.info('Redis is ready')
    except Exception:
        logging.info('Redis is not ready')
        raise Exception('Redis is not ready')


if __name__ == '__main__':
    wait_for_redis()
