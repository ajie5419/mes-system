from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from middleware.rbac import require_permission
from services import bigscreen_service

router = APIRouter(prefix="/api/v1/bigscreen", tags=["数据大屏"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db), _=Depends(require_permission("dashboard:read"))):
    """大屏汇总数据"""
    return bigscreen_service.get_bigscreen_data(db)
