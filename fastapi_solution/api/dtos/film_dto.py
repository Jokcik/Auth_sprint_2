from pydantic import BaseModel

from models.film import Film


class FilmResponseDto(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0.0

    @classmethod
    def from_model(cls, model: Film):
        return cls(id=model.uuid, title=model.title, imdb_rating=model.rating)
