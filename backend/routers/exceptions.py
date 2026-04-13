from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from services import exception_service

router = APIRouter(prefix="/api/v1/exceptions", tags=["exceptions"])


class ExceptionCreate(BaseModel):
    wo_id: Optional[int] = None
    exception_type: str
    severity: str = "medium"
    description: str
    department_id: int
    reporter_id: int
    assigned_to: Optional[int] = None


class ExceptionUpdate(BaseModel):
    exception_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None


class ExceptionResolve(BaseModel):
    root_cause: str
    solution: str


@router.get("/")
def list_exceptions(exception_type: Optional[str] = None, department_id: Optional[int] = None,
                     status: Optional[str] = None, severity: Optional[str] = None,
                     page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    total, items = exception_service.get_exceptions(db, exception_type, department_id, status, severity, page, page_size)
    return {
        "total": total, "page": page, "page_size": page_size,
        "items": [{
            "id": e.id, "wo_id": e.wo_id, "exception_type": e.exception_type,
            "severity": e.severity, "description": e.description,
            "department_id": e.department_id,
            "department_name": e.department.name if e.department else None,
            "reporter_id": e.reporter_id,
            "reporter_name": e.reporter.display_name if e.reporter else None,
            "assigned_to": e.assigned_to,
            "assignee_name": e.assignee.display_name if e.assignee else None,
            "status": e.status, "root_cause": e.root_cause, "solution": e.solution,
            "resolved_at": str(e.resolved_at) if e.resolved_at else None,
            "created_at": str(e.created_at), "updated_at": str(e.updated_at),
        } for e in items],
    }


@router.post("/")
def create_exception(data: ExceptionCreate, db: Session = Depends(get_db)):
    exc = exception_service.create_exception(db, **data.model_dump())
    return {"id": exc.id, "message": "上报成功"}


@router.get("/stats")
def exception_stats(db: Session = Depends(get_db)):
    return exception_service.get_exception_stats(db)


@router.get("/{exc_id}")
def get_exception(exc_id: int, db: Session = Depends(get_db)):
    exc = exception_service.get_exception(db, exc_id)
    if not exc:
        raise HTTPException(status_code=404, detail="异常不存在")
    return {
        "id": exc.id, "wo_id": exc.wo_id, "exception_type": exc.exception_type,
        "severity": exc.severity, "description": exc.description,
        "department_id": exc.department_id,
        "department_name": exc.department.name if exc.department else None,
        "reporter_id": exc.reporter_id,
        "reporter_name": exc.reporter.display_name if exc.reporter else None,
        "assigned_to": exc.assigned_to,
        "assignee_name": exc.assignee.display_name if exc.assignee else None,
        "status": exc.status, "root_cause": exc.root_cause, "solution": exc.solution,
        "resolved_at": str(exc.resolved_at) if exc.resolved_at else None,
        "created_at": str(exc.created_at), "updated_at": str(exc.updated_at),
    }


@router.put("/{exc_id}")
def update_exception(exc_id: int, data: ExceptionUpdate, db: Session = Depends(get_db)):
    exc = exception_service.update_exception(db, exc_id, **data.model_dump(exclude_unset=True))
    if not exc:
        raise HTTPException(status_code=404, detail="异常不存在")
    return {"message": "更新成功"}


@router.put("/{exc_id}/escalate")
def escalate_exception(exc_id: int, db: Session = Depends(get_db)):
    exc = exception_service.escalate(db, exc_id)
    if not exc:
        raise HTTPException(status_code=404, detail="异常不存在")
    return {"message": "已升级", "new_severity": exc.severity}


@router.put("/{exc_id}/resolve")
def resolve_exception(exc_id: int, data: ExceptionResolve, db: Session = Depends(get_db)):
    exc = exception_service.resolve(db, exc_id, data.root_cause, data.solution)
    if not exc:
        raise HTTPException(status_code=404, detail="异常不存在")
    return {"message": "已解决"}
