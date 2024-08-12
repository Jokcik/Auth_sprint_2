import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tests.functional.settings import test_settings

TEST_DATABASE_URL = f"postgresql+asyncpg://{test_settings.db_user}:{test_settings.db_password}@{test_settings.db_host}:{test_settings.db_port}/{test_settings.db_name}"

@pytest_asyncio.fixture(scope="function")
async def pg_pool():
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
    await engine.dispose()
