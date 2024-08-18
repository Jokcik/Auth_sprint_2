from functools import lru_cache
from typing import List, cast, Optional

from elasticsearch import NotFoundError
from fastapi import Depends

from core.config import ProjectConfig, get_project_config
from db.elastic import (
    get_elastic,
    SearchEngineService,
    ElasticSearchService,
    SearchEngine,
)
from db.redis import get_cache, CacheService, Cache, CacheServiceImpl
from models.genre import Genre
from services.abstract_service import AbstractGenreService


class GenreService(AbstractGenreService):
    def __init__(
        self,
        cache_service: CacheService,
        search_service: SearchEngineService,
        config: ProjectConfig,
    ):
        super().__init__(cache_service, search_service, config)

    async def get_all_genres(self, page: int, size: int) -> List[Genre]:
        query_cache = {page: page, size: size}
        response = await self.cache_service.get_list(query_cache)
        if response is not None:
            return cast(List[Genre], response)

        request_body = self.search_service.get_request_body()
        self.search_service.paginate(request_body, page, size)
        search_response = await self.search_service.search(body=request_body)

        response = self.search_service.get_raw_list_response(search_response)
        response = [Genre(**hit) for hit in response]

        await self.cache_service.set_list(query_cache, response)
        return response

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        if response := await self.cache_service.get(genre_id):
            return response
        try:
            search_response = await self.search_service.get(id=genre_id)
        except NotFoundError:
            return

        response = self.search_service.get_raw_retrieve_response(search_response)
        response = Genre(**response)

        await self.cache_service.set(genre_id, response)
        return response


@lru_cache()
def get_genre_service(
    es: SearchEngine = Depends(get_elastic),
    cache: Cache = Depends(get_cache),
    config: ProjectConfig = Depends(get_project_config),
) -> GenreService:
    cache_service = CacheServiceImpl(
        cache, prefix="genre_", model=Genre, field_pk="uuid"
    )
    search_service = ElasticSearchService(es, index=config.es_genre_index)

    return GenreService(
        search_service=search_service, cache_service=cache_service, config=config
    )
