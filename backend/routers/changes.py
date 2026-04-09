from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.change_record import (
    ChangeCreate,
    ChangeConfirmInput,
    ChangeRecordResponse,
)
from services import change_service

router = APIRouter(prefix="/api/v1/changes", tags=["变更控制"])


@router.post("/", response_model=ChangeRecordResponse, status_code=201)
def create_change(data: ChangeCreate, db: Session = Depends(get_db)):
    """
    发起变更申请。
    系统将自动锁定关联工单，并向指定部门生成待确认通知。
    工单锁定期间，所有进度汇报将被禁止。
    """
    try:
        change = change_service.create_change(db, data)
        return change
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ChangeRecordResponse])
def list_changes(
    wo_id: Optional[int] = Query(None, description="按工单 ID 筛选"),
    db: Session = Depends(get_db),
):
    """获取变更记录列表"""
    return change_service.get_changes(db, wo_id=wo_id)


@router.post("/{change_id}/confirm", response_model=ChangeRecordResponse)
def confirm_change(
    change_id: int,
    data: ChangeConfirmInput,
    db: Session = Depends(get_db),
):
    """
    部门负责人确认变更。
    当所有被通知部门全部确认后，工单自动解锁，恢复正常流转。
    """
    try:
        change = change_service.confirm_change(db, change_id, data)
        return change
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
