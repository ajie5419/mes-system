"""数据分析服务：工单/部门/异常/进度/KPI 统计"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, and_, or_, Date
from datetime import datetime, timedelta, date
from models.work_order import WorkOrder
from models.milestone import Milestone
from models.progress import ProgressReport
from models.exception import Exception as MESException
from models.department import Department
from constants import WorkOrderStatus


# ── 工单分析 ──

def get_wo_completion_trend(db: Session, start_date: date, end_date: date, group_by: str = "day"):
    """工单完成趋势"""
    q_created = db.query(
        func.date(WorkOrder.created_at).label("dt"),
        func.count().label("created")
    ).filter(func.date(WorkOrder.created_at).between(start_date, end_date))

    q_completed = db.query(
        func.date(WorkOrder.actual_delivery_date).label("dt"),
        func.count().label("completed")
    ).filter(
        WorkOrder.actual_delivery_date.isnot(None),
        func.date(WorkOrder.actual_delivery_date).between(start_date, end_date)
    )

    if group_by == "week":
        q_created = q_created.group_by(func.strftime("%Y-W%W", WorkOrder.created_at))
        q_completed = q_completed.group_by(func.strftime("%Y-W%W", WorkOrder.actual_delivery_date))
    elif group_by == "month":
        q_created = q_created.group_by(func.strftime("%Y-%m", WorkOrder.created_at))
        q_completed = q_completed.group_by(func.strftime("%Y-%m", WorkOrder.actual_delivery_date))
    else:
        q_created = q_created.group_by(func.date(WorkOrder.created_at))
        q_completed = q_completed.group_by(func.date(WorkOrder.actual_delivery_date))

    created_data = {str(r.dt) if r.dt else "": r.created for r in q_created.all()}
    completed_data = {str(r.dt) if r.dt else "": r.completed for r in q_completed.all()}

    all_dates = sorted(set(created_data.keys()) | set(completed_data.keys()))
    return [{"date": d, "created": created_data.get(d, 0), "completed": completed_data.get(d, 0)} for d in all_dates]


def get_wo_cycle_time(db: Session):
    """工单平均周期（天）"""
    rows = db.query(
        WorkOrder.wo_number,
        WorkOrder.created_at,
        WorkOrder.actual_delivery_date,
        func.julianday(WorkOrder.actual_delivery_date) - func.julianday(WorkOrder.created_at).label("cycle")
    ).filter(
        WorkOrder.actual_delivery_date.isnot(None),
        WorkOrder.created_at.isnot(None)
    ).all()

    if not rows:
        return {"avg_cycle_days": 0, "distribution": []}

    cycles = [float(r.cycle or 0) for r in rows]
    avg = sum(cycles) / len(cycles)

    # 按区间分布
    buckets = {"0-3天": 0, "4-7天": 0, "8-14天": 0, "15-30天": 0, "30天以上": 0}
    for c in cycles:
        if c <= 3: buckets["0-3天"] += 1
        elif c <= 7: buckets["4-7天"] += 1
        elif c <= 14: buckets["8-14天"] += 1
        elif c <= 30: buckets["15-30天"] += 1
        else: buckets["30天以上"] += 1

    return {"avg_cycle_days": round(avg, 1), "distribution": buckets}


def get_wo_on_time_rate(db: Session):
    """按时交付率"""
    total = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.planned_delivery_date.isnot(None)
    ).scalar() or 0

    if total == 0:
        return {"total": 0, "on_time": 0, "rate": 0}

    on_time = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.planned_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date <= WorkOrder.planned_delivery_date
    ).scalar() or 0

    return {"total": total, "on_time": on_time, "rate": round(on_time / total * 100, 1)}


def get_wo_overdue_analysis(db: Session):
    """延期分析"""
    rows = db.query(
        Department.name.label("department"),
        WorkOrder.wo_number,
        func.julianday(WorkOrder.actual_delivery_date) - func.julianday(WorkOrder.planned_delivery_date).label("delay_days")
    ).outerjoin(
        Department, WorkOrder.technical_manager_id == Department.id
    ).filter(
        WorkOrder.planned_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date > WorkOrder.planned_delivery_date
    ).all()

    by_dept = {}
    for r in rows:
        dept = r.department or "未分配"
        if dept not in by_dept:
            by_dept[dept] = {"count": 0, "total_delay": 0}
        by_dept[dept]["count"] += 1
        by_dept[dept]["total_delay"] += float(r.delay_days or 0)

    return [
        {"department": k, "count": v["count"], "avg_delay": round(v["total_delay"] / v["count"], 1)}
        for k, v in sorted(by_dept.items(), key=lambda x: -x[1]["count"])
    ]


# ── 部门分析 ──

def get_department_workload(db: Session):
    """部门工作量分布"""
    depts = db.query(Department).filter(Department.is_active == True).all()
    result = []
    for d in depts:
        in_progress = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.status == WorkOrderStatus.IN_PROGRESS.value
        ).scalar() or 0
        backlog = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.status == WorkOrderStatus.BACKLOG.value
        ).scalar() or 0
        completed = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.status == WorkOrderStatus.COMPLETED.value
        ).scalar() or 0
        result.append({
            "department": d.name,
            "in_progress": in_progress,
            "backlog": backlog,
            "completed": completed,
        })
    return result


def get_department_efficiency(db: Session):
    """部门效率（完成率、平均处理时间）"""
    depts = db.query(Department).filter(Department.is_active == True).all()
    result = []
    for d in depts:
        total_wo = db.query(func.count(WorkOrder.id)).scalar() or 0
        completed_wo = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.status == WorkOrderStatus.COMPLETED.value
        ).scalar() or 0
        completion_rate = round(completed_wo / total_wo * 100, 1) if total_wo else 0

        avg_cycle_row = db.query(
            func.avg(
                func.julianday(WorkOrder.actual_delivery_date) - func.julianday(WorkOrder.created_at)
            )
        ).filter(
            WorkOrder.actual_delivery_date.isnot(None),
            WorkOrder.created_at.isnot(None)
        ).scalar()
        avg_cycle = round(float(avg_cycle_row or 0), 1)

        result.append({
            "department": d.name,
            "completion_rate": completion_rate,
            "avg_cycle_days": avg_cycle,
        })
    return result


# ── 异常分析 ──

def get_exception_trend(db: Session, days: int = 30):
    """异常趋势（按天）"""
    start = date.today() - timedelta(days=days)
    rows = db.query(
        func.date(MESException.created_at).label("dt"),
        func.count().label("count"),
        func.sum(case((MESException.status == "resolved", 1), else_=0)).label("resolved")
    ).filter(
        func.date(MESException.created_at) >= start
    ).group_by(func.date(MESException.created_at)).all()

    return [{"date": str(r.dt), "count": r.count, "resolved": r.resolved or 0} for r in rows]


def get_exception_resolution_time(db: Session):
    """异常平均解决时间"""
    rows = db.query(
        MESException.exception_type,
        func.avg(func.julianday(MESException.resolved_at) - func.julianday(MESException.created_at)).label("avg_days")
    ).filter(
        MESException.resolved_at.isnot(None)
    ).group_by(MESException.exception_type).all()

    return [{"type": r.exception_type, "avg_resolution_days": round(float(r.avg_days or 0), 1)} for r in rows]


def get_exception_by_type(db: Session):
    """异常类型分布"""
    rows = db.query(
        MESException.exception_type,
        func.count().label("count")
    ).group_by(MESException.exception_type).all()

    return [{"type": r.exception_type, "count": r.count} for r in rows]


def get_exception_by_department(db: Session):
    """部门异常排名"""
    rows = db.query(
        Department.name,
        func.count(MESException.id).label("count")
    ).join(MESException, MESException.department_id == Department.id).group_by(
        Department.name
    ).order_by(func.count(MESException.id).desc()).all()

    return [{"department": r.name, "count": r.count} for r in rows]


# ── 进度分析 ──

def get_progress_streak(db: Session, days: int = 30):
    """进度汇报连续性"""
    start = date.today() - timedelta(days=days)
    rows = db.query(
        func.date(ProgressReport.report_date).label("dt"),
        func.count().label("reports")
    ).filter(
        func.date(ProgressReport.report_date) >= start
    ).group_by(func.date(ProgressReport.report_date)).all()

    report_dates = {r.dt: r.reports for r in rows}
    result = []
    d = start
    while d <= date.today():
        result.append({
            "date": str(d),
            "has_report": d in report_dates,
            "count": report_dates.get(d, 0)
        })
        d += timedelta(days=1)

    # 统计连续未汇报天数
    current_streak = 0
    max_streak = 0
    for item in result:
        if not item["has_report"]:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return {"calendar": result, "max_streak_no_report": max_streak, "total_days": days}


def get_milestone_completion_rate(db: Session):
    """里程碑完成率排名"""
    rows = db.query(
        Milestone.node_name,
        func.count().label("total"),
        func.sum(case((Milestone.status == "Completed", 1), else_=0)).label("completed")
    ).group_by(Milestone.node_name).all()

    result = []
    for r in rows:
        rate = round(r.completed / r.total * 100, 1) if r.total else 0
        result.append({"node_name": r.node_name, "total": r.total, "completed": r.completed, "rate": rate})

    return sorted(result, key=lambda x: x["rate"])


# ── 综合 KPI ──

def get_kpi_dashboard(db: Session):
    """核心 KPI 仪表盘"""
    on_time = get_wo_on_time_rate(db)
    cycle = get_wo_cycle_time(db)

    total_exceptions = db.query(func.count(MESException.id)).scalar() or 0
    resolved_exceptions = db.query(func.count(MESException.id)).filter(
        MESException.status.in_(["resolved", "closed"])
    ).scalar() or 0

    overdue_wo = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.planned_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date.isnot(None),
        WorkOrder.actual_delivery_date > WorkOrder.planned_delivery_date
    ).scalar() or 0

    milestone_data = get_milestone_completion_rate(db)
    avg_milestone_rate = round(sum(m["rate"] for m in milestone_data) / len(milestone_data), 1) if milestone_data else 0

    return {
        "on_time_delivery_rate": on_time["rate"],
        "avg_cycle_days": cycle["avg_cycle_days"],
        "total_exceptions": total_exceptions,
        "exception_resolution_rate": round(resolved_exceptions / total_exceptions * 100, 1) if total_exceptions else 0,
        "overdue_work_orders": overdue_wo,
        "milestone_completion_rate": avg_milestone_rate,
        "total_work_orders": db.query(func.count(WorkOrder.id)).scalar() or 0,
        "completed_work_orders": db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.status == WorkOrderStatus.COMPLETED.value
        ).scalar() or 0,
    }
