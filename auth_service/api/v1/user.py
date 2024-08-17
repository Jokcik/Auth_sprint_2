from fastapi import APIRouter, Depends, HTTPException, status
from opentelemetry import trace

from schemas.role import RoleAssignment
from utils.pagination_params import PaginateQueryParams
from services.user_service import UserService, get_user_service, UserNotFoundError, UserWrongPasswordError, \
    UserUniqueError
from schemas.user import User, UserPagination, UserUpdate, UserCreate, UserChangePassword, UserLoginHistoryPagination
from typing import Annotated
from uuid import UUID

router = APIRouter()
tracer = trace.get_tracer(__name__)


# todo sqlalchemy errors handler when debug mode on
@router.post("/", response_model=User,
             summary="Создание нового пользователя",
             description="Создает нового пользователя в системе. Требует административных прав.")
def create_users(user_data: UserCreate, user_service: UserService = Depends()):
    with tracer.start_as_current_span("create_users") as span:
        try:
            user = user_service.create_user(user_data)
        except UserUniqueError as error:
            span.record_exception(error)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=str(error))
        return user


@router.get("/", response_model=UserPagination,
            summary="Получение списка пользователей",
            description="Возвращает список пользователей с поддержкой пагинации. Требует административных прав.")
def get_users(pagination: Annotated[PaginateQueryParams, Depends()],
              user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("get_users") as span:
        span.set_attribute("page", pagination.page_number)
        span.set_attribute("size", pagination.page_size)
        users, total = user_service.get_users(pagination.page_number, pagination.page_size)
        return UserPagination(
            items=users,
            total=total,
            page=pagination.page_number,
            size=pagination.page_size
        )


@router.get("/{user_id}", response_model=User,
            summary="Получение информации о конкретном пользователе",
            description="Возвращает подробную информацию о пользователе по его идентификатору.")
def get_user(user_id: UUID,
             user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user_id", user_id)
        try:
            return user_service.get_user_by_id(user_id)
        except UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.put("/{user_id}", summary="Обновление данных пользователя",
            description="Обновляет информацию о пользователе.")
def update_user(user_id: UUID, user_data: UserUpdate,
                user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("update_user") as span:
        span.set_attribute("user_id", user_id)
        try:
            return user_service.update_user(user_id, user_data)
        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.delete("/{user_id}",
               summary="Удаление пользователя",
               description="Удаляет пользователя из системы. Требует административных прав.")
def delete_user(user_id: UUID,
                user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("delete_user") as span:
        span.set_attribute("user_id", user_id)
        try:
            return user_service.delete_role(user_id)
        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/{user_id}/change-password",
             summary="Изменение пароля пользователя",
             description="Позволяет пользователю изменить свой пароль. Требует подтверждения текущего пароля.",
             status_code=status.HTTP_200_OK)
def change_password(user_id: UUID, password_data: UserChangePassword,
                    user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("change_password") as span:
        span.set_attribute("user_id", user_id)
        try:
            return user_service.change_password(user_id, password_data)
        except (UserNotFoundError, UserWrongPasswordError) as error:
            span.record_exception(error)
            if isinstance(error, UserNotFoundError):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if isinstance(error, UserWrongPasswordError):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Wrong password",
                    headers={"WWW-Authenticate": "Bearer"},
                )


@router.get("/{user_id}/login-history", response_model=UserLoginHistoryPagination,
            summary="Получение истории входов пользователя",
            description="Возвращает историю входов пользователя в систему с поддержкой пагинации.")
def get_user_login_history(user_id: UUID, pagination: Annotated[PaginateQueryParams, Depends()],
                           user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("get_user_login_history") as span:
        span.set_attribute("user_id", user_id)
        try:
            users, total = user_service.login_history(user_id, pagination.page_number, pagination.page_size)
            return UserLoginHistoryPagination(
                items=users,
                total=total,
                page=pagination.page_number,
                size=pagination.page_size
            )

        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/{user_id}/roles", response_model=User,
             summary="Назначение роли пользователю",
             description="Добавляет указанную роль пользователю. Требует административных прав.")
def add_roles_to_user(user_id: UUID, role_assignment: RoleAssignment,
                      user_service: UserService = Depends(get_user_service)):
    with tracer.start_as_current_span("add_roles_to_user") as span:
        span.set_attribute("user_id", user_id)
        try:
            user = user_service.get_user_by_id(user_id)
        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user = user_service.add_role_to_user(user_id, role_assignment.role_id)
        return user  # todo может лучше отдавать роли конекретного юзера?


@router.delete("/{user_id}/roles/{role_id}", response_model=User,
               summary="Удаление роли у пользователя",
               description="Удаляет указанную роль у пользователя. Требует административных прав.")
def remove_role_from_user(user_id: UUID, role_id: UUID,
                          user_service: UserService = Depends()):
    with tracer.start_as_current_span("remove_role_from_user") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("role_id", role_id)
        try:
            return user_service.remove_role_from_user(user_id, role_id)
        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
