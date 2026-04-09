import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request

from models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: Optional[int],
    username: str,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    detail: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    """记录一条审计日志。"""
    entry = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=json.dumps(detail, ensure_ascii=False, default=str) if detail else None,
        ip_address=_extract_ip(request) if request else None,
        user_agent=request.headers.get("user-agent", "")[:500] if request else None,
    )
    db.add(entry)
    db.commit()


def get_logs(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """分页查询审计日志。"""
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if start_date:
        q = q.filter(AuditLog.created_at >= start_date)
    if end_date:
        q = q.filter(AuditLog.created_at <= end_date)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_log(db: Session, log_id: int) -> Optional[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.id == log_id).first()


def _extract_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
