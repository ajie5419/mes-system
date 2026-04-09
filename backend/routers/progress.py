from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.progress import ProgressReportCreate, ProgressReportResponse
from services import progress_service

router = APIRouter(prefix="/api/v1/progress", tags=["进度汇报"])


@router.post("/report", response_model=ProgressReportResponse, status_code=201)
def submit_progress(data: ProgressReportCreate, db: Session = Depends(get_db)):
    """
    班组提交每日进度汇报。
    若工单处于锁定状态（存在未确认的变更），系统将拒绝本次汇报。
    汇报成功后自动触发偏差核对与工单健康度重算。
    """
    try:
        report = progress_service.submit_progress(db, data)
        return report
    except PermissionError as e:
        raise HTTPException(status_code=423, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{wo_id}", response_model=List[ProgressReportResponse])
def get_progress(wo_id: int, db: Session = Depends(get_db)):
    """获取某工单的所有进度汇报记录"""
    return progress_service.get_progress_by_wo(db, wo_id)
