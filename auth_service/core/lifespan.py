from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import asyncio as aioredis
from sqlalchemy import create_engine

from core.config import settings
from db import redis, database


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis_client = aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf-8",
        decode_responses=True,
    )

    database.engine = create_engine(settings.database_url)

    yield

    await redis.redis_client.close()
