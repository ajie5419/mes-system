from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import print_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission

router = APIRouter(prefix="/api/v1/print", tags=["打印模板"])


@router.get("/work-order/{wo_id}")
def get_work_order_print_data(
    wo_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("work_orders:read")),
):
    """获取工单打印数据（结构化 JSON，供前端渲染打印预览）"""
    try:
        return print_service.get_work_order_print_data(db, wo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/progress-report/{wo_id}")
def get_progress_report_print_data(
    wo_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("progress:read")),
):
    """获取进度报告打印数据"""
    try:
        return print_service.get_progress_report_print_data(db, wo_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
