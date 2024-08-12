from uuid import UUID

from pydantic import BaseModel
from typing import List
from schemas.permission import Permission


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase):
    id: UUID
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


class RolePagination(BaseModel):
    items: List[Role]
    total: int
    page: int
    size: int


class RoleAssignment(BaseModel):
    role_id: UUID
