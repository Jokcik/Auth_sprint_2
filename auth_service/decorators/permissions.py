from functools import wraps
from uuid import UUID
from typing import Optional

from fastapi import status, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from core.roles import UserRole
from core.config import settings  # Предполагается, что у вас есть файл конфигурации
from models.user import User
from utils.auth_request import AuthRequest
from utils.exceptions import AuthException
from services.user_service import UserService, get_user_service


def roles_required(roles_list: list[UserRole]):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            user: User = kwargs.get('request').custom_user
            if not user or not set(role.name for role in user.roles).intersection([x.value for x in roles_list]):
                raise AuthException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have enough permissions to access this resource."
                )
            return await function(*args, **kwargs)

        return wrapper

    return decorator


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
            self,
            request: Request,
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
            user_service: UserService = Depends(get_user_service)
    ) -> Optional[User]:
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            user = await self.verify_jwt(credentials.credentials, user_service)
            if not user:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return user
        else:
            return None

    async def verify_jwt(self, jwt_token: str, user_service: UserService) -> Optional[User]:
        try:
            payload = jwt.decode(jwt_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: UUID = UUID(payload.get('sub'))
            if user_id:
                user = user_service.get_user_by_id(user_id)
                return user
        except JWTError:
            return None
        return None


async def get_current_user_global(request: AuthRequest, user: Optional[User] = Depends(JWTBearer())):
    request.custom_user = user
