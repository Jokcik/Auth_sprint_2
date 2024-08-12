from pydantic import BaseModel
from typing import List
from uuid import UUID


class PermissionBase(BaseModel):
    name: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: UUID

    class Config:
        from_attributes = True


class PermissionPagination(BaseModel):
    items: List[Permission]
    total: int
    page: int
    size: int
