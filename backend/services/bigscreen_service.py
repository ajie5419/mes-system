from sqlalchemy.orm import Session
from sqlalchemy import func, case, cast, Date
from datetime import datetime, timedelta
from models.work_order import WorkOrder
from models.audit_log import AuditLog
from constants import WorkOrderStatus, HealthStatus


def get_bigscreen_data(db: Session):
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)

    # ── 基础计数 ──
    total = db.query(func.count(WorkOrder.id)).scalar() or 0
    in_progress = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.IN_PROGRESS.value
    ).scalar() or 0
    completed = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.COMPLETED.value
    ).scalar() or 0
    today_new = db.query(func.count(WorkOrder.id)).filter(
        cast(WorkOrder.created_at, Date) == today
    ).scalar() or 0
    today_done = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == WorkOrderStatus.COMPLETED.value,
        cast(WorkOrder.actual_delivery_date, Date) == today
    ).scalar() or 0

    # 延期 = 进行中且计划交期已过
    overdue = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_([WorkOrderStatus.IN_PROGRESS.value, WorkOrderStatus.BACKLOG.value]),
        WorkOrder.planned_delivery_date < today,
        WorkOrder.planned_delivery_date.isnot(None)
    ).scalar() or 0

    # ── 完成率 / 延期率 ──
    completion_rate = round(completed / total * 100, 1) if total > 0 else 0
    overdue_rate = round(overdue / total * 100, 1) if total > 0 else 0

    # ── 健康度分布 ──
    health_dist = {}
    for hs in HealthStatus:
        health_dist[hs.value] = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.health_status == hs.value
        ).scalar() or 0

    # ── 部门分布（基于技术经理） ──
    from models.user import User
    dept_dist = db.query(User.department, func.count(WorkOrder.id)).join(
        User, WorkOrder.technical_manager_id == User.id
    ).group_by(User.department).all()
    department_distribution = {d: c for d, c in dept_dist}

    # ── 近 7 天趋势 ──
    trend = []
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        daily_new = db.query(func.count(WorkOrder.id)).filter(
            cast(WorkOrder.created_at, Date) == d
        ).scalar() or 0
        daily_done = db.query(func.count(WorkOrder.id)).filter(
            cast(WorkOrder.actual_delivery_date, Date) == d
        ).scalar() or 0
        trend.append({
            "date": d.strftime("%m-%d"),
            "new": daily_new,
            "completed": daily_done,
        })

    # ── 优先级分布 ──
    priority_dist = db.query(WorkOrder.priority, func.count(WorkOrder.id)).group_by(
        WorkOrder.priority
    ).all()
    priority_distribution = {str(p): c for p, c in priority_dist}

    # ── 最近操作日志 (10条) ──
    recent_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
    log_list = [
        {
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "resource_type": log.resource_type,
            "detail": (log.detail or "")[:80],
            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
        }
        for log in recent_logs
    ]

    return {
        "total": total,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "today_new": today_new,
        "today_done": today_done,
        "completion_rate": completion_rate,
        "overdue_rate": overdue_rate,
        "health_distribution": health_dist,
        "department_distribution": department_distribution,
        "trend": trend,
        "priority_distribution": priority_distribution,
        "recent_logs": log_list,
    }
