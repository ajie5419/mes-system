from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- 发起变更 ----------
class ChangeCreate(BaseModel):
    wo_id: int
    change_type: str           # 技术变更/工艺变更/计划变更
    description: str
    initiated_by: Optional[int] = None
    notify_departments: Optional[List[str]] = None


# ---------- 确认变更 ----------
class ChangeConfirmInput(BaseModel):
    department: str
    confirmed_by: Optional[int] = None


# ---------- 确认记录响应 ----------
class ConfirmationResponse(BaseModel):
    id: int
    department: str
    confirmed: bool
    confirmed_by: Optional[int]
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- 变更记录响应 ----------
class ChangeRecordResponse(BaseModel):
    id: int
    wo_id: int
    change_type: str
    description: str
    initiated_by: Optional[int]
    status: str
    created_at: datetime
    confirmations: List[ConfirmationResponse] = []

    class Config:
        from_attributes = True
