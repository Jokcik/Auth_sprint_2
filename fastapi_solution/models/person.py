from typing import Optional

from pydantic import BaseModel, Field


class PersonFilm(BaseModel):
    uuid: str
    roles: list[str]


class Person(BaseModel):
    uuid: str
    name: str
    films: list[PersonFilm]
