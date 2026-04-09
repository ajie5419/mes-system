from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from services import audit_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission

router = APIRouter(prefix="/api/v1/audit", tags=["操作日志"])


class AuditLogItem(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    action: str
    resource_type: str
    resource_id: Optional[int]
    detail: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogDetail(AuditLogItem):
    pass


class PaginatedAuditLogs(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuditLogItem]


@router.get("/logs", response_model=PaginatedAuditLogs)
def list_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="ISO 日期，如 2026-01-01"),
    end_date: Optional[str] = Query(None, description="ISO 日期，如 2026-12-31"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("audit:read")),
):
    """查询操作日志"""
    sd = datetime.fromisoformat(start_date) if start_date else None
    ed = datetime.fromisoformat(end_date) if end_date else None
    result = audit_service.get_logs(db, user_id=user_id, action=action,
                                     resource_type=resource_type,
                                     start_date=sd, end_date=ed,
                                     page=page, page_size=page_size)
    return result


@router.get("/logs/{log_id}", response_model=AuditLogDetail)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("audit:read")),
):
    """查看单条日志详情"""
    log = audit_service.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log
