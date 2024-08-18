from http import HTTPStatus

from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dtos.person_dto import PersonResponseDto
from models.pagination_params import PaginateQueryParams
from services.person_service import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[PersonResponseDto],
    summary="Получение списка персон",
    description="Позволяет получить список всех персон",
)
async def get_persons(pagination: Annotated[PaginateQueryParams, Depends()],
                      service: PersonService = Depends(get_person_service)):
    return await service.get_all_persons(pagination.page_number, pagination.page_size)


@router.get(
    "/search",
    response_model=List[PersonResponseDto],
    summary="Поиск персон",
    description="Позволяет найти персон по имени",
)
async def search_persons(query: str, service: PersonService = Depends(get_person_service)):
    return await service.search_persons(query)


@router.get(
    "/{person_id}",
    response_model=PersonResponseDto,
    summary="Получение персоны по ID",
    description="Позволяет получить персону по её ID",
)
async def get_person(person_id: str, service: PersonService = Depends(get_person_service)):
    if person := await service.get_person_by_id(person_id):
        return person
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

