from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import alert_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["看板与预警"])


@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    """
    获取全局看板健康状态。
    返回各状态工单的数量分布（正常/预警/延期/锁定/今日完工）。
    """
    return alert_service.get_dashboard_health(db)


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """看板汇总：健康度 + 今日漏报预警"""
    health = alert_service.get_dashboard_health(db)
    alerts = alert_service.check_unreported_tasks(db)

    return {
        "health": health,
        "unreported_alerts": alerts,
        "unreported_count": len(alerts),
    }
