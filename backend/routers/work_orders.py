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

router = APIRouter(prefix="/api/v1/work-orders", tags=["工单管理"])


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(data: WorkOrderCreate, db: Session = Depends(get_db)):
    """创建新工单，自动生成工单号并初始化里程碑节点"""
    wo = work_order_service.create_work_order(db, data)
    return wo


@router.get("/", response_model=PaginatedWorkOrders)
def list_work_orders(
    status: Optional[str] = Query(None, description="按状态筛选: Backlog/InProgress/Blocked/Completed/Archived"),
    keyword: Optional[str] = Query(None, description="按项目名/工单号/客户名搜索"),
    is_delayed: Optional[bool] = Query(None, description="仅显示延期工单"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取工单列表，支持多条件筛选与分页"""
    total, items = work_order_service.get_work_orders(
        db, status=status, keyword=keyword, is_delayed=is_delayed,
        page=page, page_size=page_size,
    )
    return PaginatedWorkOrders(total=total, page=page, page_size=page_size, items=items)


@router.get("/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(wo_id: int, db: Session = Depends(get_db)):
    """获取工单详情，包含所有里程碑节点与实时进度"""
    wo = work_order_service.get_work_order(db, wo_id)
    if not wo:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    return wo


@router.put("/{wo_id}", response_model=WorkOrderResponse)
def update_work_order(wo_id: int, data: WorkOrderUpdate, db: Session = Depends(get_db)):
    """更新工单基本信息"""
    wo = work_order_service.update_work_order(db, wo_id, data)
    if not wo:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    return wo


@router.delete("/{wo_id}", status_code=204)
def delete_work_order(wo_id: int, db: Session = Depends(get_db)):
    """删除工单及其所有关联数据"""
    success = work_order_service.delete_work_order(db, wo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"工单 ID {wo_id} 不存在")
    return None
