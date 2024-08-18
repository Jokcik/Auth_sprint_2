from abc import ABC, abstractmethod, ABCMeta
from typing import Optional, List

from elasticsearch import AsyncElasticsearch

from core.config import ProjectConfig
from utils.film_util import BaseSortEnum

es: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> Optional[AsyncElasticsearch]:
    return es


class SearchEngine(ABC):
    @abstractmethod
    async def search(self, index=None, body: dict = None) -> List:
        pass

    @abstractmethod
    async def get(self, index=None, id: str = None):
        pass


class ElasticSearch(SearchEngine):
    def __init__(self, es: AsyncElasticsearch, config: ProjectConfig):
        self.es = es
        self.config = config

    async def search(self, index=None, body: dict = None) -> List:
        return await self.es.search(index, body)

    async def get(self, index=None, id: str = None) -> dict:
        return await self.es.get(index, id)


class SearchSortMixin(ABC):
    @staticmethod
    @abstractmethod
    def sort(request_body: dict, sort: BaseSortEnum):
        pass


class ElasticSearchSortMixin(SearchSortMixin):
    @staticmethod
    def sort(request_body: dict, sort: BaseSortEnum) -> dict:
        request_body["sort"] = sort.to_elasticsearch()
        return request_body


class SearchFilterMixin(ABC):
    @staticmethod
    @abstractmethod
    def filter(request_body, field, value):
        pass

    @staticmethod
    @abstractmethod
    def related_filter(
        request_body: {}, related_field: str, inner_field: str, filter_value: str
    ) -> dict:

        pass


class ElasticSearchFilterMixin(SearchFilterMixin):
    @staticmethod
    def filter(request_body, field, value):
        return {"query": {"match": {field: value}}}

    @staticmethod
    def related_filter(
        request_body, related_field: str, inner_field: str, filter_value: str
    ):
        request_body["query"] = {
            "nested": {
                "path": related_field,
                "query": {"term": {f"{related_field}.{inner_field}": filter_value}},
                "inner_hits": {},
            }
        }
        return request_body


class SearchEngineService(ABC):
    @property
    @abstractmethod
    def raw_request_body(self):
        pass

    def __init__(self, search_engine: SearchEngine, index=None):
        self.search_engine = search_engine
        self.index = index

    @abstractmethod
    async def search(self, body: dict):
        pass

    @abstractmethod
    async def get(self, id):
        pass

    @abstractmethod
    def paginate(self, request_body, from_, size):
        pass

    @staticmethod
    @abstractmethod
    def get_raw_list_response(es_response):
        pass

    @staticmethod
    @abstractmethod
    def get_raw_retrieve_response(es_response):
        pass

    def get_request_body(
        self,
    ):
        return self.raw_request_body.copy()


class ElasticSearchService(SearchEngineService):
    raw_request_body = {"query": {"match_all": {}}}

    async def search(self, body):
        return await self.search_engine.search(index=self.index, body=body)

    async def get(self, id):
        return await self.search_engine.get(index=self.index, id=id)

    def paginate(self, request_body, page, size):
        request_body["from"] = (page - 1) * size
        request_body["size"] = size

    @staticmethod
    def get_raw_list_response(es_response):
        return [hit["_source"] for hit in es_response["hits"]["hits"]]

    @staticmethod
    def get_raw_retrieve_response(es_response):
        return es_response["_source"]


class FilmSearchEngineService(
    SearchEngineService, SearchSortMixin, SearchFilterMixin, metaclass=ABCMeta
):
    pass


class PersonSearchEngineService(SearchEngineService, SearchFilterMixin, metaclass=ABCMeta):
    pass


class FilmElasticSearchService(
    FilmSearchEngineService,
    ElasticSearchService,
    ElasticSearchSortMixin,
    ElasticSearchFilterMixin,
):
    pass


class PersonElasticSearchService(
    PersonSearchEngineService,
    ElasticSearchService,
    ElasticSearchFilterMixin,
):
    pass
