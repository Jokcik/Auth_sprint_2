from pydantic import BaseModel


class GenreResponseDto(BaseModel):
    uuid: str
    name: str
