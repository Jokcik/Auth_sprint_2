import logging
from http import HTTPStatus

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from api.dtos.film_dto import FilmResponseDto
from models.pagination_params import PaginateQueryParams
from services.film_service import FilmService, get_film_service

from core.jwt import security_jwt
from utils.film_util import FilmSortEnum

router = APIRouter()


@router.get(
    "/",
    response_model=List[FilmResponseDto],
    summary="Получение списка фильмов",
    description="Позволяет получить список всех фильмов",
)
async def get_films(pagination: Annotated[PaginateQueryParams, Depends()],
                    user: Annotated[dict, Depends(security_jwt)],
                    sort: FilmSortEnum = '',
                    genre: UUID = '',
                    service: FilmService = Depends(get_film_service)):
    logging.debug(f"User: {user}")
    films = await service.get_all_films(sort, genre, pagination.page_number, pagination.page_size)
    return [
        FilmResponseDto.from_model(film) for film in films
    ]


@router.get(
    "/search",
    response_model=List[FilmResponseDto],
    summary="Поиск фильмов",
    description="Позволяет найти фильмы по названию",
)
# todo pagin - 1 next previous
async def search_films(query: str, service: FilmService = Depends(get_film_service)):
    films = await service.search_films(query)
    return [
        FilmResponseDto.from_model(film) for film in films
    ]


@router.get(
    "/{film_id}",
    response_model=FilmResponseDto,
    summary="Получение фильма по ID",
    description="Позволяет получить фильм по его ID",
)
async def get_film(film_id: str, service: FilmService = Depends(get_film_service)):
    if film := await service.get_film_by_id(film_id):
        return FilmResponseDto.from_model(film)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

