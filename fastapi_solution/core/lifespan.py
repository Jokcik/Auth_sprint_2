from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis

from core.config import RedisConfig, ElasticConfig
from db import redis, elastic


@asynccontextmanager
async def lifespan(app: FastAPI):
    redisConfig = RedisConfig()
    redis.redis = Redis(host=redisConfig.host, port=redisConfig.port)

    esConfig = ElasticConfig()
    elastic.es = AsyncElasticsearch(hosts=[f'{esConfig.host}:{esConfig.port}'])

    yield

    await redis.redis.close()
    await elastic.es.close()
