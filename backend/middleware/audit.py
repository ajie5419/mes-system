from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session

from services import audit_service


def record(
    db: Session,
    user,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    detail: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    """便捷函数：在业务操作成功后手动调用记录审计日志。

    user: 可以是 User 模型实例，或 None（如 login 前的场景，此时需传 username）。
    """
    audit_service.log_action(
        db=db,
        user_id=user.id if user else None,
        username=(user.username if user else "anonymous"),
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        request=request,
    )
