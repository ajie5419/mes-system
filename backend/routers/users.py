from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate
from services import user_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission
from middleware.audit import record
from fastapi import Request

router = APIRouter(prefix="/api/v1/users", tags=["组织架构管理"])

@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("users:create"))):
    """新增用户"""
    u = user_service.create_user(db, data)
    record(db, current_user, "create", "user", u.id, {"username": data.username, "display_name": data.display_name}, request)
    return u

@router.get("/", response_model=List[UserResponse])
def list_users(
    department: Optional[str] = Query(None, description="按部门筛选"),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("users:read")),
):
    """查阅名册"""
    return user_service.get_users(db, department=department)

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("users:update"))):
    """修改用户信息"""
    user = user_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="该用户不在名册中")
    record(db, current_user, "update", "user", user_id, data.model_dump(exclude_unset=True), request)
    return user
