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
from services.auth_service import get_current_user
from middleware.rbac import require_permission
from middleware.audit import record
from fastapi import Request

router = APIRouter(prefix="/api/v1/changes", tags=["变更控制"])


@router.post("/", response_model=ChangeRecordResponse, status_code=201)
def create_change(data: ChangeCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("changes:create"))):
    """发起变更申请"""
    try:
        change = change_service.create_change(db, data)
        record(db, current_user, "create", "change", change.id, {"description": data.description}, request)
        return change
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ChangeRecordResponse])
def list_changes(
    wo_id: Optional[int] = Query(None, description="按工单 ID 筛选"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("changes:read")),
):
    """获取变更记录列表"""
    return change_service.get_changes(db, wo_id=wo_id)


@router.post("/{change_id}/confirm", response_model=ChangeRecordResponse)
def confirm_change(
    change_id: int,
    data: ChangeConfirmInput,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("changes:confirm")),
):
    """部门负责人确认变更"""
    try:
        change = change_service.confirm_change(db, change_id, data)
        record(db, current_user, "update", "change", change_id, {"confirmed": data.model_dump()}, request)
        return change
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
