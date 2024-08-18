from pydantic import BaseModel


class PersonFilmDto(BaseModel):
    uuid: str
    roles: list[str]


class PersonResponseDto(BaseModel):
    uuid: str
    name: str
    films: list[PersonFilmDto]