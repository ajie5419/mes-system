from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    action = Column(String(20), nullable=False, index=True)
    resource_type = Column(String(30), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
