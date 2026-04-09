"""数据分析路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from database import get_db
from services import analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


def _parse_date(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("/kpi")
def kpi_dashboard(db: Session = Depends(get_db)):
    return analytics_service.get_kpi_dashboard(db)


@router.get("/work-orders/trend")
def wo_trend(
    start_date: str = Query(None),
    end_date: str = Query(None),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
):
    sd = _parse_date(start_date) or (date.today() - __import__("datetime").timedelta(days=30))
    ed = _parse_date(end_date) or date.today()
    return analytics_service.get_wo_completion_trend(db, sd, ed, group_by)


@router.get("/work-orders/cycle-time")
def wo_cycle_time(db: Session = Depends(get_db)):
    return analytics_service.get_wo_cycle_time(db)


@router.get("/work-orders/on-time-rate")
def wo_on_time_rate(db: Session = Depends(get_db)):
    return analytics_service.get_wo_on_time_rate(db)


@router.get("/work-orders/overdue")
def wo_overdue(db: Session = Depends(get_db)):
    return analytics_service.get_wo_overdue_analysis(db)


@router.get("/department/workload")
def dept_workload(db: Session = Depends(get_db)):
    return analytics_service.get_department_workload(db)


@router.get("/department/efficiency")
def dept_efficiency(db: Session = Depends(get_db)):
    return analytics_service.get_department_efficiency(db)


@router.get("/exceptions/trend")
def exception_trend(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return analytics_service.get_exception_trend(db, days)


@router.get("/exceptions/resolution")
def exception_resolution(db: Session = Depends(get_db)):
    return analytics_service.get_exception_resolution_time(db)


@router.get("/exceptions/by-type")
def exception_by_type(db: Session = Depends(get_db)):
    return analytics_service.get_exception_by_type(db)


@router.get("/exceptions/by-department")
def exception_by_department(db: Session = Depends(get_db)):
    return analytics_service.get_exception_by_department(db)


@router.get("/progress/streak")
def progress_streak(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return analytics_service.get_progress_streak(db, days)


@router.get("/milestone/completion")
def milestone_completion(db: Session = Depends(get_db)):
    return analytics_service.get_milestone_completion_rate(db)
