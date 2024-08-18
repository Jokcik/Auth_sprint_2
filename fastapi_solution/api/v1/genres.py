from http import HTTPStatus

from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dtos.genre_dto import GenreResponseDto
from models.pagination_params import PaginateQueryParams
from services.genre_service import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[GenreResponseDto],
    summary="Получение списка жанров",
    description="Позволяет получить список всех жанров",
)
async def get_genres(pagination: Annotated[PaginateQueryParams, Depends()],
                     service: GenreService = Depends(get_genre_service)):
    return await service.get_all_genres(pagination.page_number, pagination.page_size)


@router.get(
    "/{genre_id}",
    response_model=GenreResponseDto,
    summary="Получение жанра по ID",
    description="Позволяет получить жанр по его ID",
)
async def get_genre(genre_id: str, service: GenreService = Depends(get_genre_service)):
    if genre := await service.get_genre_by_id(genre_id):
        return genre
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
