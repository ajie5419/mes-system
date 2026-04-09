from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User
from models.token import RevokedToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _build_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = {**data, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int, username: str, role: str) -> str:
    return _build_token(
        {"sub": str(user_id), "username": username, "role": role, "type": "access"},
        timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return _build_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证凭据")

    payload = _decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌类型错误")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def refresh_access_token(refresh_token: str, db: Session) -> str:
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌类型错误")

    jti = payload.get("jti")
    if jti and db.query(RevokedToken).filter_by(token_jti=jti).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已被撤销")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return create_access_token(user.id, user.username, user.role)
