from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import get_current_user
from services import permission_service


def require_permission(perm_code: str):
    """FastAPI dependency: check if current user's role has the required permission."""
    async def _check(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
        if not permission_service.check_permission(db, current_user.role, perm_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {perm_code}",
            )
        return current_user
    return _check
