from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..constants import Department, UserRole

class UserBase(BaseModel):
    username: str
    display_name: str
    department: Department
    role: UserRole

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    department: Optional[Department] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
