from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.user import User
from schemas.user import UserResponse
from services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_current_user, refresh_access_token,
)
from constants import Department, UserRole
from middleware.audit import record

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    username: str
    display_name: str = None
    password: str
    department: Department = None
    role: UserRole = UserRole.WORKER


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        display_name=req.display_name,
        hashed_password=hash_password(req.password),
        department=req.department,
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.role),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已禁用")
    record(db, user, "login", "user", user.id, {"username": user.username}, request)
    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.role),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh")
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    new_access = refresh_access_token(req.refresh_token, db)
    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
