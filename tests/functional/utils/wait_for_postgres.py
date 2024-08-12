import logging

import backoff
import psycopg2
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = Field(..., alias='POSTGRES_DB')
    db_user: str = Field(..., alias='POSTGRES_USER')
    db_password: str = Field(..., alias='POSTGRES_PASSWORD')
    db_host: str = Field('localhost', alias='POSTGRES_HOST')
    db_port: int = Field(5432, alias='POSTGRES_PORT')


@backoff.on_exception(
    backoff.expo,
    exception=(psycopg2.OperationalError,),
    max_tries=8,
    factor=2,
)
def wait_for_postgres():
    settings = Settings()
    conn_string = f"dbname={settings.db_name} user={settings.db_user} password={settings.db_password} host={settings.db_host} port={settings.db_port}"

    try:
        conn = psycopg2.connect(conn_string)
        conn.close()
        logging.info('PostgreSQL is ready')
    except psycopg2.OperationalError:
        logging.info('PostgreSQL is not ready')
        raise


if __name__ == '__main__':
    wait_for_postgres()