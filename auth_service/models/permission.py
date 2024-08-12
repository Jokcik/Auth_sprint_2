from sqlalchemy import Column, String
from db.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
