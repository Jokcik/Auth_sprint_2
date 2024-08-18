import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from opentelemetry import trace
from pydantic import BaseModel, BeforeValidator

from core.config import settings
from db import redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # todo нужен ли ?


class TokenValidationError(Exception):
    pass


def coerce_to_str(data: Any) -> Any:
    # if isinstance(data, FieldObject?): # todo
    #     return str(data)
    return str(data)


CoercedStr = Annotated[str, BeforeValidator(coerce_to_str)]


class AbstractAuthService(ABC):

    @abstractmethod
    async def register(self, db_user):
        pass

    @abstractmethod
    async def login(self, db_user):
        pass

    @abstractmethod
    async def invalidate_token(self, token: str):
        pass


class AuthSubSchema(BaseModel):
    sub: CoercedStr

    class Config:
        from_attributes = True


class AuthJWTService(AbstractAuthService):

    def __init__(self):
        self.tracer = trace.get_tracer(f'{__name__}:{self.__class__.__name__}')

    async def register(self, db_user):
        with self.tracer.start_as_current_span("register") as span:
            access_token = self.create_access_token(data=AuthSubSchema(sub=db_user.id))
            refresh_token = self.create_refresh_token(data=AuthSubSchema(sub=db_user.id))

            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def login(self, db_user):
        with self.tracer.start_as_current_span("login") as span:
            access_token = self.create_access_token(data=AuthSubSchema(sub=db_user.id))
            refresh_token = self.create_refresh_token(data=AuthSubSchema(sub=db_user.id))
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def refresh_token(self, refresh_token: str):
        with self.tracer.start_as_current_span("refresh_token") as span:
            return await self.refresh_access_token(refresh_token)

    async def logout(self, token: str):
        with self.tracer.start_as_current_span("logout") as span:
            await self.invalidate_token(token)

    def create_access_token(self, data: AuthSubSchema, expires_delta: timedelta | None = None):
        with self.tracer.start_as_current_span("create_access_token") as span:
            data = data.model_dump()
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            try:
                encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
                return encoded_jwt
            except Exception as e:
                span.record_exception(e)
                raise TokenValidationError(f"Failed to create access token: {str(e)}")

    def create_refresh_token(self, data: AuthSubSchema):
        with self.tracer.start_as_current_span("create_refresh_token") as span:
            data = data.dict()
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
            to_encode.update({"exp": expire})
            try:
                encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
                return encoded_jwt
            except Exception as e:
                span.record_exception(e)
                raise TokenValidationError(f"Failed to create refresh token: {str(e)}")

    async def get_current_user_id(self, token: str) -> int:
        with self.tracer.start_as_current_span("get_current_user_id") as span:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            try:
                payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
                id: str = payload.get("sub")
                if id is None:
                    logging.info(f"Invalid token payload {payload}")
                    raise credentials_exception
                if await redis.redis_client.get(f"blacklist:{token}"):
                    logging.info("Token is blacklisted")
                    raise credentials_exception
            except JWTError as e:
                span.record_exception(e)
                logging.warning(f"Invalid token: {str(e)}")
                raise credentials_exception

            return id

    async def invalidate_token(self, token: str):
        with self.tracer.start_as_current_span("invalidate_token") as span:
            try:
                await redis.redis_client.setex(f"blacklist:{token}", settings.access_token_expire_minutes * 60, "1")
            except Exception as e:
                span.record_exception(e)
                logging.info(f"Failed to invalidate token: {str(e)}")
                raise TokenValidationError(f"Failed to invalidate token: {str(e)}")

    async def refresh_access_token(self, refresh_token: str):
        with self.tracer.start_as_current_span("refresh_access_token") as span:
            try:
                payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
                id: str = payload.get("sub")
                if id is None:
                    logging.info(f"Invalid refresh token payload {payload}")
                    raise TokenValidationError("Invalid refresh token")
            except JWTError as e:
                span.record_exception(e)
                logging.info(f"Invalid refresh token: {str(e)}")
                raise TokenValidationError("Invalid refresh token")
            return id


@lru_cache
def get_auth_service(auth_service: AuthJWTService = Depends()):
    return auth_service
