
from sqlalchemy import Engine
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine: Engine | None = None
Base = declarative_base()


class CustomSession(Session):
    def __init__(self, bind=None, **kwargs):
        super().__init__(bind=bind, **kwargs)

    def commit(self):
        try:
            super().commit()
        except StatementError as e:
            raise e.orig


def get_db():
    db = CustomSession(autocommit=settings.database_autocommit,
                       autoflush=settings.database_autoflush,
                       bind=engine)
    try:
        yield db
    finally:
        db.close()
