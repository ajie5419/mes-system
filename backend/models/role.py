from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    is_system = Column(Boolean, default=False)
    level = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
