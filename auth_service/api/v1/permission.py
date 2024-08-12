from fastapi import APIRouter, Depends, Query

from core.roles import UserRole
from decorators.permissions import roles_required
from services.permission_service import PermissionService
from schemas.permission import PermissionCreate, PermissionUpdate, Permission, PermissionPagination
from uuid import UUID

from utils.auth_request import AuthRequest

router = APIRouter()


@router.post("/", response_model=Permission,
             summary="Создание нового разрешения",
             description="Создает новое разрешение в системе. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def create_permission(
    *,
    request: AuthRequest,
    permission_data: PermissionCreate,
    permission_service: PermissionService = Depends()
):
    permission = permission_service.create_permission(permission_data)
    return permission


@router.get("/", response_model=PermissionPagination,
            summary="Получение списка разрешений",
            description="Возвращает список всех разрешений в системе с поддержкой пагинации.")
@roles_required(roles_list=[UserRole.ADMIN])
async def get_roles(
    *,
    request: AuthRequest,
    permission_service: PermissionService = Depends(),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1)
):
    roles, total = permission_service.get_permissions(page, size)
    return PermissionPagination(
        items=roles,
        total=total,
        page=page,
        size=size
    )


@router.get("/{permission_id}",
            summary="Получение информации о конкретном разрешении",
            description="Возвращает подробную информацию о разрешении по его идентификатору.")
@roles_required(roles_list=[UserRole.ADMIN])
async def get_permission(
    *,
    request: AuthRequest,
    permission_id: UUID,
    permission_service: PermissionService = Depends()
):
    return permission_service.get_permission(permission_id)


@router.put("/{permission_id}",
            summary="Обновление разрешения",
            description="Обновляет информацию о существующем разрешении. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def update_permission(
    *,
    request: AuthRequest,
    permission_id: UUID,
    permission_data: PermissionUpdate,
    permission_service: PermissionService = Depends()
):
    return permission_service.update_permission(permission_id, permission_data)


@router.delete("/{permission_id}",
               summary="Удаление разрешения",
               description="Удаляет разрешение из системы. Требует административных прав.")
@roles_required(roles_list=[UserRole.ADMIN])
async def delete_permission(
    *,
    request: AuthRequest,
    permission_id: UUID,
    permission_service: PermissionService = Depends()
):
    return permission_service.delete_permission(permission_id)
