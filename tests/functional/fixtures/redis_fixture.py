import pytest_asyncio
from redis.asyncio import Redis

from tests.functional.settings import test_settings

@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield client
    await client.flushdb()
    await client.close()