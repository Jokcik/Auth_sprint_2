from fastapi import Depends
from opentelemetry import trace
from sqlalchemy.orm import Session

from core.roles import UserRole
from db.database import get_db
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from models.permission import Permission
from uuid import UUID


class RoleService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.tracer = trace.get_tracer(f'{__name__}:{self.__class__.__name__}')

    def create_role(self, role_data: RoleCreate):
        with self.tracer.start_as_current_span("create_role") as span:
            role = Role(name=role_data.name, description=role_data.description)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role

    def get_roles(self, page: int, size: int):
        with self.tracer.start_as_current_span("get_roles") as span:
            query = self.db.query(Role)
            total = query.count()
            roles = query.offset((page - 1) * size).limit(size).all()
            return roles, total

    def get_role(self, role_id: UUID):
        with self.tracer.start_as_current_span("get_role") as span:
            return self.db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, name: UserRole):
        with self.tracer.start_as_current_span("get_role_by_name") as span:
            return self.db.query(Role).filter(Role.name == name.value).first()

    def update_role(self, role_id: UUID, role_data: RoleUpdate):
        with self.tracer.start_as_current_span("update_role") as span:
            role = self.get_role(role_id)
            if role:
                role.name = role_data.name
                role.description = role_data.description
                self.db.commit()
                self.db.refresh(role)
            return role

    def delete_role(self, role_id: UUID):
        with self.tracer.start_as_current_span("delete_role") as span:
            role = self.get_role(role_id)
            if role:
                self.db.delete(role)
                self.db.commit()
            return role

    def add_permission_to_role(self, role_id: UUID, permission_id: UUID):
        with self.tracer.start_as_current_span("add_permission_to_role") as span:
            role = self.get_role(role_id)
            permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
            if role and permission:
                role.permissions.append(permission)
                self.db.commit()
            return role

    def remove_permission_from_role(self, role_id: UUID, permission_id: UUID):
        with self.tracer.start_as_current_span("remove_permission_from_role") as span:
            role = self.get_role(role_id)
            permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
            if role and permission:
                role.permissions.remove(permission)
                self.db.commit()

            return role
