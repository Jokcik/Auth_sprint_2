from typing import Optional, List

from pydantic import BaseModel


class FilmGenre(BaseModel):
    uuid: str
    name: str


class FilmPerson(BaseModel):
    uuid: str
    name: str


class Film(BaseModel):
    uuid: str
    title: str
    description: Optional[str]
    rating: float
    type: str
    genres: List[FilmGenre]
    actors: List[FilmPerson] = []
    directors: List[FilmPerson] = []
    writers: List[FilmPerson] = []
