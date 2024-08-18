from functools import lru_cache
from typing import List, Union, cast

from elasticsearch import NotFoundError
from fastapi import Depends

from core.config import ProjectConfig, get_project_config
from db.elastic import (
    get_elastic,
    PersonSearchEngineService,
    SearchEngine,
    PersonElasticSearchService,
)
from db.redis import CacheService, Cache, get_cache, CacheServiceImpl
from models.person import Person
from services.abstract_service import AbstractPersonService


class PersonService(AbstractPersonService):
    def __init__(
        self,
        cache_service: CacheService,
        search_service: PersonSearchEngineService,
        config: ProjectConfig,
    ):
        super().__init__(cache_service, search_service, config)

    async def get_all_persons(self, page: int, size: int) -> List[Person]:
        query_cache = {page: page, size: size}
        response = await self.cache_service.get_list(query_cache)
        if response is not None:
            return cast(List[Person], response)

        request_body = self.search_service.get_request_body()
        self.search_service.paginate(request_body, page, size)

        search_response = await self.search_service.search(body=request_body)
        response = self.search_service.get_raw_list_response(search_response)
        response = [Person(**hit) for hit in response]

        await self.cache_service.set_list(query_cache, response)
        return response

    async def get_person_by_id(self, person_id: str) -> Union[Person, None]:
        if response := await self.cache_service.get(person_id):
            return response

        try:
            search_response = await self.search_service.get(id=person_id)
        except NotFoundError:
            return

        response = self.search_service.get_raw_retrieve_response(search_response)
        response = Person(**response)

        await self.cache_service.set(person_id, response)
        return response

    async def search_persons(self, query: str) -> List[Person]:
        if response := await self.cache_service.get_list(query):
            return cast(List[Person], response)

        request_body = self.search_service.get_request_body()
        request_body = self.search_service.filter(request_body, "name", query)
        search_response = await self.search_service.search(request_body)
        response = self.search_service.get_raw_list_response(search_response)
        response = [Person(**hit) for hit in response]
        await self.cache_service.set_list(query, response)
        return response


@lru_cache()
def get_person_service(
    es: SearchEngine = Depends(get_elastic),
    cache: Cache = Depends(get_cache),
    config: ProjectConfig = Depends(get_project_config),
) -> PersonService:
    cache_service = CacheServiceImpl(
        cache, prefix="person_", model=Person, field_pk="uuid"
    )
    search_service = PersonElasticSearchService(es, index=config.es_person_index)
    return PersonService(
        search_service=search_service, cache_service=cache_service, config=config
    )
