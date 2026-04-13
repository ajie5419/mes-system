from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=True) # 开发阶段允许为空
    
    department = Column(String(50), nullable=True, index=True)
    role = Column(String(20), nullable=False, index=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
