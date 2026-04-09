"""数据导出路由"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from middleware.rbac import require_permission

from services import export_service

router = APIRouter(prefix="/export", tags=["数据导出"])


def _make_response(data: bytes, filename_prefix: str):
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{filename_prefix}_{date_str}.xlsx"
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/work-orders")
async def export_work_orders(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    is_delayed: Optional[bool] = None,
    db: Session = Depends(get_db),
    _=require_permission("work_orders:read"),
):
    filters = {}
    if status:
        filters["status"] = status
    if keyword:
        filters["keyword"] = keyword
    if is_delayed is not None:
        filters["is_delayed"] = is_delayed
    data = export_service.export_work_orders_to_excel(db, filters)
    return _make_response(data, "工单列表")


@router.get("/work-orders/{wo_id}")
async def export_work_order_detail(
    wo_id: int,
    db: Session = Depends(get_db),
    _=require_permission("work_orders:read"),
):
    try:
        data = export_service.export_work_order_detail_to_excel(db, wo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _make_response(data, f"工单详情_{wo_id}")


@router.get("/progress")
async def export_progress(
    db: Session = Depends(get_db),
    _=require_permission("work_orders:read"),
):
    data = export_service.export_progress_to_excel(db, {})
    return _make_response(data, "进度汇总")


@router.get("/audit-logs")
async def export_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=require_permission("audit:read"),
):
    from datetime import datetime as dt
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if action:
        filters["action"] = action
    if resource_type:
        filters["resource_type"] = resource_type
    if start_date:
        filters["start_date"] = dt.fromisoformat(start_date)
    if end_date:
        filters["end_date"] = dt.fromisoformat(end_date)
    data = export_service.export_audit_logs_to_excel(db, filters)
    return _make_response(data, "操作日志")


@router.get("/users")
async def export_users(
    db: Session = Depends(get_db),
    _=require_permission("users:read"),
):
    data = export_service.export_users_to_excel(db)
    return _make_response(data, "用户列表")
