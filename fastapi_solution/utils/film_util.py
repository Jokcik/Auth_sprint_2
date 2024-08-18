from abc import abstractmethod, ABCMeta
from enum import Enum, EnumMeta


class BaseSortEnumMeta(ABCMeta, EnumMeta):
    """ABC and Enum got different meta classes"""

    pass


class BaseSortEnum(str, Enum, metaclass=BaseSortEnumMeta):
    @abstractmethod
    def to_elasticsearch(self):
        pass


class FilmSortEnum(BaseSortEnum):
    imdb_rating_asc = "imdb"
    imdb_rating_desc = "-imdb"

    # mapper? todo
    def to_elasticsearch(self):
        return {
            self.imdb_rating_asc: {"rating": "asc"},
            self.imdb_rating_desc: {"rating": "desc"},
        }[self]
