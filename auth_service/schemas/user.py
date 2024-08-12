import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from schemas.role import Role


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: UUID
    is_active: bool
    roles: List[Role]

    class Config:
        from_attributes = True


class UserPagination(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str


class UserLoginHistory(BaseModel):
    id: UUID
    user_id: UUID
    ip_address: str
    user_agent: str
    login_at: datetime.datetime

    class Config:
        from_attributes = True


class UserLoginHistoryPagination(BaseModel):
    items: List[UserLoginHistory]
    total: int
    page: int
    size: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
