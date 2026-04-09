from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# ---------- 进度汇报 ----------
class ProgressReportCreate(BaseModel):
    wo_id: int
    milestone_id: int
    reported_by: Optional[int] = None
    team_name: Optional[str] = None
    completion_rate: float        # 0-100
    remark: Optional[str] = None
    report_date: date


# ---------- 进度响应 ----------
class ProgressReportResponse(BaseModel):
    id: int
    wo_id: int
    milestone_id: int
    reported_by: Optional[int]
    team_name: Optional[str]
    completion_rate: float
    remark: Optional[str]
    report_date: date
    created_at: datetime

    class Config:
        from_attributes = True
