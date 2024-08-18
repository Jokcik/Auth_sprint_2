from functools import lru_cache
from typing import List, Union, Literal, cast, Optional
from uuid import UUID

from elasticsearch import NotFoundError
from fastapi import Depends

from core.config import ProjectConfig, get_project_config
from db.elastic import (
    get_elastic,
    FilmSearchEngineService,
    FilmElasticSearchService,
    SearchEngine,
)
from db.redis import get_cache, Cache, CacheService, CacheServiceImpl
from models.film import Film
from services.abstract_service import AbstractFilmService
from utils.film_util import FilmSortEnum


class FilmService(AbstractFilmService):
    def __init__(
        self,
        cache_service: CacheService,
        search_service: FilmSearchEngineService,
        config: ProjectConfig,
    ):
        super().__init__(cache_service, search_service, config)

    async def get_all_films(
        self, sort: Union[FilmSortEnum, Literal[""]], genre: UUID, page: int, size: int
    ) -> List[Film]:
        query_cache = {"sort": sort, "genre": str(genre), "page": page, "size": size}
        response = await self.cache_service.get_list(query_cache)
        if response is not None:
            return cast(List[Film], response)

        request_body = self.search_service.get_request_body()
        self.search_service.paginate(request_body, page, size)
        if sort:
            self.search_service.sort(request_body, sort)
        if genre:
            self.search_service.related_filter(request_body, "genres", "uuid", genre)

        search_response = await self.search_service.search(body=request_body)
        response = self.search_service.get_raw_list_response(search_response)
        response = [Film(**hit) for hit in response]

        await self.cache_service.set_list(query_cache, response)
        return response

    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        if response := await self.cache_service.get(film_id):
            return response
        try:
            search_response = await self.search_service.get(id=film_id)
        except NotFoundError:
            return

        response = self.search_service.get_raw_retrieve_response(search_response)
        response = Film(**response)

        await self.cache_service.set(film_id, response)
        return response

    async def search_films(self, query: str) -> List[Film]:
        if response := await self.cache_service.get_list(query):
            return cast(List[Film], response)

        request_body = self.search_service.get_request_body()
        request_body = self.search_service.filter(request_body, "title", query)
        search_response = await self.search_service.search(request_body)
        response = self.search_service.get_raw_list_response(search_response)
        response = [Film(**hit) for hit in response]

        await self.cache_service.set_list(query, response)
        return response


@lru_cache()
def get_film_service(
    es: SearchEngine = Depends(get_elastic),
    cache: Cache = Depends(get_cache),
    config: ProjectConfig = Depends(get_project_config),
) -> FilmService:
    cache_service = CacheServiceImpl(cache, prefix="film_", model=Film, field_pk="uuid")
    search_service = FilmElasticSearchService(es, index=config.es_film_index)
    return FilmService(
        search_service=search_service, cache_service=cache_service, config=config
    )
