from sqlalchemy.orm import Session
from datetime import date
from models.work_order import WorkOrder
from models.milestone import Milestone
from models.progress import ProgressReport
from schemas.progress import ProgressReportCreate
from services.work_order_service import recalculate_wo_health


def submit_progress(db: Session, data: ProgressReportCreate) -> ProgressReport:
    """班组提交进度汇报"""
    # 1. 校验工单是否存在
    wo = db.query(WorkOrder).filter(WorkOrder.id == data.wo_id).first()
    if not wo:
        raise ValueError(f"工单 ID {data.wo_id} 不存在")

    # 2. 核心校验：工单锁定时禁止汇报
    if wo.is_locked:
        raise PermissionError(
            f"工单 {wo.wo_number} 当前处于锁定状态（存在未确认的变更），"
            "请先处理变更确认后再汇报进度。"
        )

    # 3. 校验里程碑是否存在
    milestone = db.query(Milestone).filter(Milestone.id == data.milestone_id).first()
    if not milestone:
        raise ValueError(f"里程碑节点 ID {data.milestone_id} 不存在")

    if milestone.wo_id != data.wo_id:
        raise ValueError("该里程碑节点不属于此工单")

    # 4. 创建汇报记录
    report = ProgressReport(
        wo_id=data.wo_id,
        milestone_id=data.milestone_id,
        reported_by=data.reported_by,
        team_name=data.team_name,
        completion_rate=data.completion_rate,
        remark=data.remark,
        report_date=data.report_date,
    )
    db.add(report)

    # 5. 更新里程碑的完成率
    milestone.completion_rate = data.completion_rate
    if data.completion_rate >= 100:
        milestone.status = "Completed"
        milestone.actual_end_date = data.report_date
    elif milestone.status == "Pending":
        milestone.status = "InProgress"
        if not milestone.actual_start_date:
            milestone.actual_start_date = data.report_date

    db.commit()

    # 6. 重新计算工单的总进度与健康状态
    recalculate_wo_health(db, data.wo_id)

    db.refresh(report)
    return report


def get_progress_by_wo(db: Session, wo_id: int):
    """获取某工单的所有进度汇报"""
    return (
        db.query(ProgressReport)
        .filter(ProgressReport.wo_id == wo_id)
        .order_by(ProgressReport.report_date.desc())
        .all()
    )
