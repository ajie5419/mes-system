from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(200), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=True)
    config_group = Column(String(50), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
