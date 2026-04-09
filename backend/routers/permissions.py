from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import get_current_user
from services import permission_service
from middleware.rbac import require_permission

router = APIRouter(prefix="/api/v1/permissions", tags=["权限管理"])


class UpdateRolePerms(BaseModel):
    permission_codes: List[str]


@router.get("/")
def list_permissions(db: Session = Depends(get_db), user=Depends(require_permission("dashboard:read"))):
    """获取所有权限（按模块分组）"""
    return permission_service.get_all_permissions(db)


@router.get("/roles")
def list_role_permissions(db: Session = Depends(get_db), user=Depends(require_permission("dashboard:read"))):
    """获取角色-权限映射"""
    return permission_service.get_role_permissions(db)


@router.put("/roles/{role}")
def update_role_perms(
    role: str,
    body: UpdateRolePerms,
    db: Session = Depends(get_db),
    user=Depends(require_permission("audit:read")),  # Admin-only guard
):
    """更新角色权限（仅 Admin）"""
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可修改角色权限")
    if role not in ("Admin", "Manager", "Worker"):
        raise HTTPException(status_code=400, detail="无效角色")
    permission_service.update_role_permissions(db, role, body.permission_codes)
    return {"message": f"角色 {role} 权限已更新"}
