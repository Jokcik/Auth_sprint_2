from abc import ABC, abstractmethod
from typing import List, Optional, Union, Literal
from uuid import UUID

from core.config import ProjectConfig
from db.elastic import (
    FilmSearchEngineService,
    PersonSearchEngineService,
    SearchEngineService,
)
from db.redis import CacheService
from models.film import Film
from models.genre import Genre
from models.person import Person
from utils.film_util import FilmSortEnum


class AbstractFilmService(ABC):
    def __init__(
            self,
            cache_service: CacheService,
            search_service: FilmSearchEngineService,
            config: ProjectConfig,
    ):
        self.cache_service = cache_service
        self.search_service = search_service
        self.config = config

    @abstractmethod
    async def get_all_films(
            self, sort: Union[FilmSortEnum, Literal[""]], genre: UUID, page: int, size: int
    ) -> List[Film]:
        pass

    @abstractmethod
    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        pass

    @abstractmethod
    async def search_films(self, query: str) -> List[Film]:
        pass


class AbstractPersonService(ABC):
    def __init__(
            self,
            cache_service: CacheService,
            search_service: PersonSearchEngineService,
            config: ProjectConfig,
    ):
        self.cache_service = cache_service
        self.search_service = search_service
        self.config = config

    @abstractmethod
    async def get_all_persons(self, page: int, size: int) -> List[Person]:
        pass

    @abstractmethod
    async def get_person_by_id(self, person_id: str) -> Union[Person, None]:
        pass

    @abstractmethod
    async def search_persons(self, query: str) -> List[Person]:
        pass


class AbstractGenreService(ABC):
    def __init__(
            self,
            cache_service: CacheService,
            search_service: SearchEngineService,
            config: ProjectConfig,
    ):
        self.cache_service = cache_service
        self.search_service = search_service
        self.config = config

    @abstractmethod
    async def get_all_genres(self, page: int, size: int) -> List[Genre]:
        pass

    @abstractmethod
    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        pass
