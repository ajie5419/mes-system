from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderResponse,
    PaginatedWorkOrders,
)
from services import work_order_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission
from middleware.audit import record
from fastapi import Request

router = APIRouter(prefix="/api/v1/work-orders", tags=["工单管理"])


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(data: WorkOrderCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("work_orders:create"))):
    """创建新工单，自动生成工单号并初始化里程碑节点"""
    wo = work_order_service.create_work_order(db, data)
    record(db, current_user, "create", "work_order", wo.id, {"project_name": data.project_name, "wo_number": wo.wo_number}, request)
    return wo


@router.get("/", response_model=PaginatedWorkOrders)
def list_work_orders(
    status: Optional[str] = Query(None, description="按状态筛选: Backlog/InProgress/Blocked/Completed/Archived"),
    keyword: Optional[str] = Query(None, description="按项目名/工单号/客户名搜索"),
    is_delayed: Optional[bool] = Query(None, description="仅显示延期工单"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("work_orders:read")),
):
    """获取工单列表，支持多条件筛选与分页"""
    total, items = work_order_service.get_work_orders(
        db, status=status, keyword=keyword, is_delayed=is_delayed,
        page=page, page_size=page_size,
    )
    return PaginatedWorkOrders(total=total, page=page, page_size=page_size, items=items)


@router.get("/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(wo_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission("work_orders:read"))):
    """获取工单详情，包含所有里程碑节点与实时进度"""
    wo = work_order_service.get_work_order(db, wo_id)
    if not wo:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    return wo


@router.put("/{wo_id}", response_model=WorkOrderResponse)
def update_work_order(wo_id: int, data: WorkOrderUpdate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("work_orders:update"))):
    """更新工单基本信息"""
    wo = work_order_service.update_work_order(db, wo_id, data)
    if not wo:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    record(db, current_user, "update", "work_order", wo_id, data.model_dump(exclude_unset=True), request)
    return wo


@router.delete("/{wo_id}", status_code=204)
def delete_work_order(wo_id: int, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("work_orders:delete"))):
    """删除工单及其所有关联数据"""
    success = work_order_service.delete_work_order(db, wo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    record(db, current_user, "delete", "work_order", wo_id, request=request)
    return None
