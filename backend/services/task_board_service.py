from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
from models.department_task import DepartmentTask


def create_task(db: Session, wo_id: int, department_id: int, task_name: str,
                description: str = None, priority: int = 3, assignee_id: int = None,
                due_date: date = None) -> DepartmentTask:
    task = DepartmentTask(
        wo_id=wo_id, department_id=department_id, task_name=task_name,
        description=description, priority=priority, assignee_id=assignee_id,
        due_date=due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, **kwargs) -> Optional[DepartmentTask]:
    task = db.query(DepartmentTask).filter(DepartmentTask.id == task_id).first()
    if not task:
        return None
    for k, v in kwargs.items():
        if v is not None:
            setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(DepartmentTask).filter(DepartmentTask.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def move_task(db: Session, task_id: int, new_status: str) -> Optional[DepartmentTask]:
    if new_status not in ("pending", "in_progress", "completed", "overdue"):
        raise ValueError(f"无效状态: {new_status}")
    task = db.query(DepartmentTask).filter(DepartmentTask.id == task_id).first()
    if not task:
        return None
    task.status = new_status
    if new_status == "completed":
        task.completed_at = datetime.now()
    db.commit()
    db.refresh(task)
    return task


def get_department_tasks(db: Session, department_id: int, status: str = None) -> List[DepartmentTask]:
    q = db.query(DepartmentTask).filter(DepartmentTask.department_id == department_id)
    if status:
        q = q.filter(DepartmentTask.status == status)
    return q.order_by(DepartmentTask.sort_order, DepartmentTask.created_at).all()


def get_all_departments_tasks(db: Session) -> list:
    """获取所有部门任务概览"""
    from models.department import Department
    depts = db.query(Department).filter(Department.is_active == True).all()
    result = []
    for dept in depts:
        tasks = db.query(DepartmentTask).filter(DepartmentTask.department_id == dept.id).all()
        counts = {"pending": 0, "in_progress": 0, "completed": 0, "overdue": 0}
        for t in tasks:
            st = t.status if t.status in counts else "pending"
            counts[st] += 1
        result.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "total": len(tasks),
            **counts,
        })
    return result
