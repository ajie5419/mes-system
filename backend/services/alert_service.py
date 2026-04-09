from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import date
from models.work_order import WorkOrder
from models.milestone import Milestone


def check_unreported_tasks(db: Session) -> List[Dict]:
    """
    每日漏报巡检逻辑
    扫描所有"进行中"的工单，找出今日未提交进度汇报的里程碑节点，
    生成告警信息列表。
    """
    from models.progress import ProgressReport

    today = date.today()
    alerts = []

    # 找出所有进行中的工单
    active_orders = (
        db.query(WorkOrder)
        .filter(WorkOrder.status.in_(["InProgress", "Backlog"]))
        .all()
    )

    for wo in active_orders:
        # 找出该工单中"进行中"但今日未汇报的里程碑
        active_milestones = (
            db.query(Milestone)
            .filter(
                Milestone.wo_id == wo.id,
                Milestone.status == "InProgress",
            )
            .all()
        )

        for ms in active_milestones:
            # 检查今日是否有汇报
            today_report = (
                db.query(ProgressReport)
                .filter(
                    ProgressReport.milestone_id == ms.id,
                    ProgressReport.report_date == today,
                )
                .first()
            )

            if not today_report:
                alerts.append({
                    "wo_number": wo.wo_number,
                    "project_name": wo.project_name,
                    "milestone": ms.node_name,
                    "production_manager_id": wo.production_manager_id,
                    "message": (
                        f"警告：工单 {wo.wo_number} 的节点 [{ms.node_name}] "
                        f"今日未提交进度汇报，请督促相关班组及时录入。"
                    ),
                })

    return alerts


def get_dashboard_health(db: Session) -> dict:
    """看板健康度统计"""
    total = db.query(WorkOrder).filter(WorkOrder.status != "Archived").count()
    green = db.query(WorkOrder).filter(
        WorkOrder.health_status == "GREEN", WorkOrder.status != "Archived"
    ).count()
    yellow = db.query(WorkOrder).filter(
        WorkOrder.health_status == "YELLOW", WorkOrder.status != "Archived"
    ).count()
    red = db.query(WorkOrder).filter(
        WorkOrder.health_status == "RED", WorkOrder.status != "Archived"
    ).count()
    locked = db.query(WorkOrder).filter(WorkOrder.is_locked == True).count()
    completed_today = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.status == "Completed",
            WorkOrder.actual_delivery_date == date.today(),
        )
        .count()
    )

    return {
        "total_active": total,
        "green": green,
        "yellow": yellow,
        "red": red,
        "locked": locked,
        "completed_today": completed_today,
    }
