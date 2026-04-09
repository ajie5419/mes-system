from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import alert_service
from services.auth_service import get_current_user
from middleware.rbac import require_permission

router = APIRouter(prefix="/api/v1/dashboard", tags=["看板与预警"])


@router.get("/health")
def get_health(db: Session = Depends(get_db), current_user = Depends(require_permission("dashboard:read"))):
    """获取全局看板健康状态"""
    return alert_service.get_dashboard_health(db)


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user = Depends(require_permission("dashboard:read"))):
    """看板汇总：健康度 + 今日漏报预警"""
    health = alert_service.get_dashboard_health(db)
    alerts = alert_service.check_unreported_tasks(db)
    return {
        "health": health,
        "unreported_alerts": alerts,
        "unreported_count": len(alerts),
    }
