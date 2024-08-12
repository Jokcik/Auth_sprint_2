import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from models.permission import Permission


role_permissions = Table('role_permissions', Base.metadata,
                         Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete="CASCADE")),
                         Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete="CASCADE"))
                         )


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


Permission.roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
