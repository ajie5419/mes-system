from sqlalchemy.orm import Session
from models.work_order import WorkOrder
from models.milestone import Milestone
from models.progress import ProgressReport
from models.change_record import ChangeRecord
from models.extra import QualityIssue
from models.user import User


def get_work_order_print_data(db: Session, wo_id: int) -> dict:
    """获取工单打印数据"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise ValueError(f"工单 ID {wo_id} 不存在")

    # 基本信息中补充关联人名
    tech_mgr = db.query(User).filter(User.id == wo.technical_manager_id).first() if wo.technical_manager_id else None
    prod_mgr = db.query(User).filter(User.id == wo.production_manager_id).first() if wo.production_manager_id else None

    milestones = db.query(Milestone).filter(Milestone.wo_id == wo_id).order_by(Milestone.sort_order).all()

    recent_reports = (
        db.query(ProgressReport)
        .filter(ProgressReport.wo_id == wo_id)
        .order_by(ProgressReport.report_date.desc(), ProgressReport.created_at.desc())
        .limit(10)
        .all()
    )
    # 补充汇报人姓名
    reports_data = []
    for r in recent_reports:
        reporter = db.query(User).filter(User.id == r.reported_by).first() if r.reported_by else None
        reports_data.append({
            "id": r.id,
            "milestone_name": db.query(Milestone.node_name).filter(Milestone.id == r.milestone_id).scalar() or "",
            "team_name": r.team_name,
            "completion_rate": r.completion_rate,
            "remark": r.remark,
            "report_date": r.report_date.isoformat() if r.report_date else None,
            "reported_by": reporter.display_name if reporter else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    changes = db.query(ChangeRecord).filter(ChangeRecord.wo_id == wo_id).order_by(ChangeRecord.created_at.desc()).all()
    changes_data = []
    for c in changes:
        initiator = db.query(User).filter(User.id == c.initiated_by).first() if c.initiated_by else None
        changes_data.append({
            "id": c.id,
            "change_type": c.change_type,
            "description": c.description,
            "status": c.status,
            "initiated_by": initiator.display_name if initiator else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    quality_issues = db.query(QualityIssue).filter(QualityIssue.wo_id == wo_id).order_by(QualityIssue.created_at.desc()).all()
    issues_data = [
        {
            "id": qi.id,
            "issue_type": qi.issue_type,
            "description": qi.description,
            "status": qi.status,
            "created_at": qi.created_at.isoformat() if qi.created_at else None,
        }
        for qi in quality_issues
    ]

    return {
        "work_order": {
            "wo_number": wo.wo_number,
            "project_name": wo.project_name,
            "customer_name": wo.customer_name,
            "priority": wo.priority,
            "status": wo.status,
            "current_stage": wo.current_stage,
            "total_progress": wo.total_progress,
            "health_status": wo.health_status,
            "planned_delivery_date": wo.planned_delivery_date.isoformat() if wo.planned_delivery_date else None,
            "actual_delivery_date": wo.actual_delivery_date.isoformat() if wo.actual_delivery_date else None,
            "technical_manager": tech_mgr.display_name if tech_mgr else None,
            "production_manager": prod_mgr.display_name if prod_mgr else None,
            "created_at": wo.created_at.isoformat() if wo.created_at else None,
            "updated_at": wo.updated_at.isoformat() if wo.updated_at else None,
        },
        "milestones": [
            {
                "id": m.id,
                "node_name": m.node_name,
                "sort_order": m.sort_order,
                "planned_start_date": m.planned_start_date.isoformat() if m.planned_start_date else None,
                "planned_end_date": m.planned_end_date.isoformat() if m.planned_end_date else None,
                "actual_start_date": m.actual_start_date.isoformat() if m.actual_start_date else None,
                "actual_end_date": m.actual_end_date.isoformat() if m.actual_end_date else None,
                "completion_rate": m.completion_rate,
                "deviation_days": m.deviation_days,
                "status": m.status,
            }
            for m in milestones
        ],
        "recent_reports": reports_data,
        "change_records": changes_data,
        "quality_issues": issues_data,
    }


def get_progress_report_print_data(db: Session, wo_id: int) -> dict:
    """获取进度汇报打印数据"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise ValueError(f"工单 ID {wo_id} 不存在")

    milestones = db.query(Milestone).filter(Milestone.wo_id == wo_id).order_by(Milestone.sort_order).all()

    reports = (
        db.query(ProgressReport)
        .filter(ProgressReport.wo_id == wo_id)
        .order_by(ProgressReport.report_date.desc(), ProgressReport.created_at.desc())
        .all()
    )
    reports_data = []
    for r in reports:
        reporter = db.query(User).filter(User.id == r.reported_by).first() if r.reported_by else None
        ms_name = db.query(Milestone.node_name).filter(Milestone.id == r.milestone_id).scalar() or ""
        reports_data.append({
            "id": r.id,
            "milestone_name": ms_name,
            "team_name": r.team_name,
            "completion_rate": r.completion_rate,
            "remark": r.remark,
            "report_date": r.report_date.isoformat() if r.report_date else None,
            "reported_by": reporter.display_name if reporter else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "work_order": {
            "wo_number": wo.wo_number,
            "project_name": wo.project_name,
            "customer_name": wo.customer_name,
            "status": wo.status,
            "total_progress": wo.total_progress,
            "health_status": wo.health_status,
            "planned_delivery_date": wo.planned_delivery_date.isoformat() if wo.planned_delivery_date else None,
        },
        "milestones": [
            {
                "node_name": m.node_name,
                "completion_rate": m.completion_rate,
                "status": m.status,
            }
            for m in milestones
        ],
        "reports": reports_data,
    }
