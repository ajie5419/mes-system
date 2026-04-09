from pydantic import BaseModel
from typing import Optional
from datetime import date


class MilestoneUpdate(BaseModel):
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    completion_rate: Optional[float] = None
    status: Optional[str] = None
