from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models.exception import Exception as MESException

SEVERITY_MAP = {"low": "medium", "medium": "high", "high": "critical", "critical": "critical"}


def create_exception(db: Session, **kwargs) -> MESException:
    exc = MESException(**kwargs)
    db.add(exc)
    db.commit()
    db.refresh(exc)
    return exc


def get_exception(db: Session, exc_id: int) -> Optional[MESException]:
    return db.query(MESException).filter(MESException.id == exc_id).first()


def get_exceptions(db: Session, exception_type: str = None, department_id: int = None,
                   status: str = None, severity: str = None, page: int = 1, page_size: int = 20):
    q = db.query(MESException)
    if exception_type:
        q = q.filter(MESException.exception_type == exception_type)
    if department_id:
        q = q.filter(MESException.department_id == department_id)
    if status:
        q = q.filter(MESException.status == status)
    if severity:
        q = q.filter(MESException.severity == severity)
    total = q.count()
    items = q.order_by(MESException.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def update_exception(db: Session, exc_id: int, **kwargs) -> Optional[MESException]:
    exc = get_exception(db, exc_id)
    if not exc:
        return None
    for k, v in kwargs.items():
        if v is not None:
            setattr(exc, k, v)
    exc.updated_at = datetime.now()
    db.commit()
    db.refresh(exc)
    return exc


def escalate(db: Session, exc_id: int) -> Optional[MESException]:
    exc = get_exception(db, exc_id)
    if not exc:
        return None
    new_sev = SEVERITY_MAP.get(exc.severity, "critical")
    exc.severity = new_sev
    exc.updated_at = datetime.now()
    db.commit()
    db.refresh(exc)
    return exc


def resolve(db: Session, exc_id: int, root_cause: str, solution: str) -> Optional[MESException]:
    exc = get_exception(db, exc_id)
    if not exc:
        return None
    exc.status = "resolved"
    exc.root_cause = root_cause
    exc.solution = solution
    exc.resolved_at = datetime.now()
    exc.updated_at = datetime.now()
    db.commit()
    db.refresh(exc)
    return exc


def get_exception_stats(db: Session) -> dict:
    total = db.query(MESException).count()
    open_count = db.query(MESException).filter(MESException.status == "open").count()
    in_progress_count = db.query(MESException).filter(MESException.status == "in_progress").count()
    resolved_count = db.query(MESException).filter(MESException.status == "resolved").count()
    closed_count = db.query(MESException).filter(MESException.status == "closed").count()

    # by type
    by_type = db.query(MESException.exception_type, func.count(MESException.id)).group_by(MESException.exception_type).all()
    type_stats = [{"type": t, "count": c} for t, c in by_type]

    # by department
    by_dept = db.query(MESException.department_id, func.count(MESException.id)).group_by(MESException.department_id).all()
    dept_stats = [{"department_id": d, "count": c} for d, c in by_dept]

    # trend: last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    trend = db.query(
        func.date(MESException.created_at).label("date"),
        func.count(MESException.id).label("count"),
    ).filter(MESException.created_at >= thirty_days_ago).group_by(func.date(MESException.created_at)).order_by("date").all()
    trend_data = [{"date": str(d), "count": c} for d, c in trend]

    # avg resolve time
    resolved = db.query(MESException).filter(MESException.resolved_at.isnot(None), MESException.created_at.isnot(None)).all()
    if resolved:
        total_hours = sum((r.resolved_at - r.created_at).total_seconds() / 3600 for r in resolved)
        avg_resolve_hours = round(total_hours / len(resolved), 1)
    else:
        avg_resolve_hours = 0

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "avg_resolve_hours": avg_resolve_hours,
        "by_type": type_stats,
        "by_department": dept_stats,
        "trend": trend_data,
    }
