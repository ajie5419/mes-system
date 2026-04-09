from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# ---------- Milestone 嵌套模型 ----------
class MilestoneInput(BaseModel):
    node_name: str
    planned_start_date: Optional[date] = None
    planned_end_date: date
    sort_order: Optional[int] = 0


class MilestoneResponse(BaseModel):
    id: int
    node_name: str
    sort_order: int
    planned_start_date: Optional[date]
    planned_end_date: date
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    completion_rate: float
    deviation_days: int
    status: str

    class Config:
        from_attributes = True


# ---------- 创建工单 ----------
class WorkOrderCreate(BaseModel):
    project_name: str
    customer_name: Optional[str] = None
    priority: Optional[int] = 3
    planned_delivery_date: date
    technical_manager_id: Optional[int] = None
    production_manager_id: Optional[int] = None
    milestones: List[MilestoneInput] = []


# ---------- 更新工单 ----------
class WorkOrderUpdate(BaseModel):
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    current_stage: Optional[str] = None
    planned_delivery_date: Optional[date] = None


# ---------- 工单响应 ----------
class WorkOrderResponse(BaseModel):
    id: int
    wo_number: str
    project_name: str
    customer_name: Optional[str]
    priority: int
    status: str
    current_stage: str
    is_locked: bool
    total_progress: float
    health_status: str
    planned_delivery_date: Optional[date]
    actual_delivery_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True


# ---------- 工单列表（不含里程碑详情） ----------
class WorkOrderListItem(BaseModel):
    id: int
    wo_number: str
    project_name: str
    customer_name: Optional[str]
    priority: int
    status: str
    current_stage: str
    is_locked: bool
    total_progress: float
    health_status: str
    planned_delivery_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 分页响应 ----------
class PaginatedWorkOrders(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[WorkOrderListItem]
