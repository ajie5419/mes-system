from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from database import get_db
from services import task_board_service

router = APIRouter(prefix="/task-board", tags=["task-board"])


class TaskCreate(BaseModel):
    wo_id: int
    department_id: int
    task_name: str
    description: Optional[str] = None
    priority: int = 3
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None
    sort_order: Optional[int] = None


class TaskMove(BaseModel):
    status: str


@router.get("/departments")
def get_departments_overview(db: Session = Depends(get_db)):
    return task_board_service.get_all_departments_tasks(db)


@router.get("/department/{dept_id}")
def get_department_tasks(dept_id: int, status: Optional[str] = None, db: Session = Depends(get_db)):
    tasks = task_board_service.get_department_tasks(db, dept_id, status)
    return [{
        "id": t.id, "wo_id": t.wo_id, "task_name": t.task_name,
        "description": t.description, "status": t.status, "priority": t.priority,
        "assignee_id": t.assignee_id,
        "assignee_name": t.assignee.display_name if t.assignee else None,
        "due_date": str(t.due_date) if t.due_date else None,
        "sort_order": t.sort_order, "created_at": str(t.created_at),
    } for t in tasks]


@router.post("/tasks")
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = task_board_service.create_task(db, **data.model_dump())
    return {"id": task.id, "message": "创建成功"}


@router.put("/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = task_board_service.update_task(db, task_id, **data.model_dump(exclude_unset=True))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "更新成功"}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not task_board_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "删除成功"}


@router.put("/tasks/{task_id}/move")
def move_task(task_id: int, data: TaskMove, db: Session = Depends(get_db)):
    try:
        task = task_board_service.move_task(db, task_id, data.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "移动成功"}
