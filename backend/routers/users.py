from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..services import user_service

router = APIRouter(prefix="/api/v1/users", tags=["组织架构管理"])

@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """新增用户：钦点新人入府"""
    return user_service.create_user(db, data)

@router.get("/", response_model=List[UserResponse])
def list_users(
    department: Optional[str] = Query(None, description="按部门筛选"),
    db: Session = Depends(get_db)
):
    """查阅名册：俯瞰府内全员"""
    return user_service.get_users(db, department=department)

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    """调动职守：修改用户信息、部门或角色"""
    user = user_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="该修行者不在名册中")
    return user
