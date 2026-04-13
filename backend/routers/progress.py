from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.progress import ProgressReportCreate, ProgressReportResponse
from services import progress_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission
from middleware.audit import record
from fastapi import Request

router = APIRouter(prefix="/api/v1/progress", tags=["进度汇报"])


@router.get("/", response_model=List[ProgressReportResponse])
def list_progress(db: Session = Depends(get_db), wo_id: int = None, current_user = Depends(require_permission("progress:read"))):
    """获取进度汇报列表，可按工单筛选"""
    if wo_id:
        return progress_service.get_progress_by_wo(db, wo_id)
    from models.progress import ProgressReport
    return db.query(ProgressReport).order_by(ProgressReport.created_at.desc()).limit(100).all()


@router.post("/report", response_model=ProgressReportResponse, status_code=201)
def submit_progress(data: ProgressReportCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("progress:report"))):
    """班组提交每日进度汇报"""
    try:
        report = progress_service.submit_progress(db, data)
        record(db, current_user, "create", "progress", report.id, {"wo_id": data.wo_id, "content": data.content}, request)
        return report
    except PermissionError as e:
        raise HTTPException(status_code=423, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{wo_id}", response_model=List[ProgressReportResponse])
def get_progress(wo_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission("progress:read"))):
    """获取某工单的所有进度汇报记录"""
    return progress_service.get_progress_by_wo(db, wo_id)
