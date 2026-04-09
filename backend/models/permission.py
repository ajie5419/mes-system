from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)  # e.g. "work_orders:read"
    name = Column(String(200), nullable=False)  # Chinese description
    module = Column(String(50), nullable=False, index=True)  # e.g. "work_orders"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False, index=True)  # Admin/Manager/Worker
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
