from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import get_db
from models.permission import Permission
from schemas.permission import PermissionCreate, PermissionUpdate
from fastapi import HTTPException, status
from uuid import UUID


class PermissionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_permission(self, permission_data: PermissionCreate):
        permission = Permission(name=permission_data.name, description=permission_data.description)
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permissions(self, page: int, size: int):
        query = self.db.query(Permission)
        total = query.count()
        roles = query.offset((page - 1) * size).limit(size).all()
        return roles, total

    def get_permission(self, permission_id: UUID):
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return permission

    def update_permission(self, permission_id: UUID, permission_data: PermissionUpdate):
        permission = self.get_permission(permission_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        permission.name = permission_data.name
        permission.description = permission_data.description
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def delete_permission(self, permission_id: UUID):
        permission = self.get_permission(permission_id)
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        self.db.delete(permission)
        self.db.commit()
        return permission
