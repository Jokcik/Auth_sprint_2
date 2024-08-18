import json
import logging
from abc import abstractmethod, ABC
from functools import lru_cache
from typing import Optional, Union, List, Type

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis

from core.config import ProjectConfig, get_project_config

redis: Optional[Redis] = None


class Cache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str:
        pass

    @abstractmethod
    async def set(self, key: str, value: str) -> None:
        pass


class RedisCache(Cache):
    def __init__(self, redis: Redis, config: ProjectConfig):
        self.redis = redis
        self.config = config

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def set(self, key: str, value: str) -> None:
        await self.redis.set(key, value, ex=self.config.cache_expire)


class CacheService(ABC):
    def __init__(self, cache: Cache, prefix: str, model: Type[BaseModel], field_pk: str = 'uuid'):
        self.cache = cache
        self.prefix = prefix
        self.model = model
        self.field_pk = field_pk

    @abstractmethod
    def get_cache_key(self, obj_id: Union[str, dict, list]) -> str:
        pass

    @abstractmethod
    async def get(self, obj_id: str) -> Union[BaseModel, None]:
        pass

    @abstractmethod
    async def get_list(self, queries_dict: Union[str, dict, list]) -> Optional[List[BaseModel]]:
        pass

    @abstractmethod
    async def set(self, obj_id: str, value: Union[BaseModel, List[BaseModel]]) -> None:
        pass

    @abstractmethod
    async def set_list(self, queries_dict: Union[str, dict, list], values: List[BaseModel]) -> None:
        pass


class CacheServiceImpl(CacheService):
    def get_cache_key(self, obj_id: Union[str, dict, list]) -> str:
        if not obj_id:
            logging.warning(f'obj_id is None: {obj_id} with prefix: {self.prefix}')

        key = obj_id
        if not isinstance(obj_id, str):
            key = json.dumps(obj_id)

        return f'{self.prefix}{key}'

    async def get(self, obj_id: str) -> Union[BaseModel, None]:
        key = self.get_cache_key(obj_id)
        cached_response = await self.cache.get(key)
        if cached_response:
            logging.info(f'found `get` cache key: {key}')
            return self.model(**json.loads(cached_response))

        logging.info(f'not found `get` cache key: {key}')
        return None

    async def get_list(self, queries_dict: Union[str, dict, list]) -> Optional[List[BaseModel]]:
        key = self.get_cache_key(queries_dict)
        cached_response = await self.cache.get(key)
        if cached_response:
            cached = json.loads(cached_response)
            if isinstance(cached, list):
                logging.info(f'found cache key: {key}')
                return [self.model(**res) for res in cached]

        logging.info(f'not found `get_list` cache key: {key}')
        return None

    async def set(self, obj_id: str, value: Union[BaseModel, List[BaseModel]]) -> None:
        key = self.get_cache_key(obj_id)
        logging.info(f'set cache key: {key}')
        await self.cache.set(key, value.model_dump_json())

    async def set_list(self, queries_dict: Union[str, dict, list], values: List[BaseModel]) -> None:
        for v in values:
            val = v.model_dump()
            if self.field_pk in val:
                obj_key = val[self.field_pk]
                key = self.get_cache_key(obj_key)
                await self.cache.set(key, v.model_dump_json())

        key = self.get_cache_key(queries_dict)
        logging.info(f'set `set_list` cache key: {key}')
        await self.cache.set(key, json.dumps([v.model_dump() for v in values]))


async def get_redis() -> Redis:
    return redis


@lru_cache()
def get_cache(config: ProjectConfig = Depends(get_project_config)) -> RedisCache:
    return RedisCache(redis, config)
