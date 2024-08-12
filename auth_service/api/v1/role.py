from uuid import UUID

from fastapi import APIRouter, Depends, Query

from core.roles import UserRole
from decorators.permissions import roles_required
from services.role_service import RoleService
from schemas.role import RoleCreate, RoleUpdate, Role, RolePagination
from utils.auth_request import AuthRequest

router = APIRouter()


@router.post("/", response_model=Role,
             summary="Создание новой роли",
             description="Создает новую роль в системе. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def create_roles(
        *,
        request: AuthRequest,
        role_data: RoleCreate,
        role_service: RoleService = Depends()
):
    role = role_service.create_role(role_data)
    return role


@router.get("/", response_model=RolePagination,
            summary="Получение списка ролей",
            description="Возвращает список всех ролей в системе с поддержкой пагинации.")
@roles_required(roles_list=[UserRole.ADMIN])
async def get_roles(
    *,
    request: AuthRequest,
    role_service: RoleService = Depends(),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1)
):
    roles, total = role_service.get_roles(page, size)
    return RolePagination(
        items=roles,
        total=total,
        page=page,
        size=size
    )


@router.get("/{role_id}",
            summary="Получение информации о конкретной роли",
            description="Возвращает подробную информацию о роли по ее идентификатору.")
@roles_required(roles_list=[UserRole.ADMIN])
async def get_role(
    *,
    request: AuthRequest,
    role_id: UUID,
    role_service: RoleService = Depends()
):
    return role_service.get_role(role_id)


@router.put("/{role_id}",
            summary="Обновление роли",
            description="Обновляет информацию о существующей роли. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def update_role(
    *,
    request: AuthRequest,
    role_id: UUID,
    role_data: RoleUpdate,
    role_service: RoleService = Depends()
):
    return role_service.update_role(role_id, role_data)


@router.delete("/{role_id}",
               summary="Удаление роли",
               description="Удаляет роль из системы. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def delete_role(
    *,
    request: AuthRequest,
    role_id: UUID,
    role_service: RoleService = Depends()
):
    return role_service.delete_role(role_id)


@router.post("/{role_id}/permissions/{permission_id}",
             summary="Добавление разрешения к роли",
             description="Добавляет указанное разрешение к роли. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def add_permission_to_role(
        *,
        request: AuthRequest,
        role_id: UUID,
        permission_id: UUID,
        role_service: RoleService = Depends()
):
    return role_service.add_permission_to_role(role_id, permission_id)


@router.delete("/{role_id}/permissions/{permission_id}",
               summary="Удаление разрешения из роли",
               description="Удаляет указанное разрешение из роли. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def remove_permission_from_role(
        *,
        request: AuthRequest,
        role_id: UUID,
        permission_id: UUID,
        role_service: RoleService = Depends()
):
    return role_service.remove_permission_from_role(role_id, permission_id)
