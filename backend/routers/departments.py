from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from services import department_service

router = APIRouter(prefix="/departments", tags=["departments"])


class DeptCreate(BaseModel):
    name: str
    code: str
    parent_id: Optional[int] = None
    sort_order: int = 0


class DeptUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    """获取部门列表（树形结构）"""
    return department_service.get_department_tree(db)


@router.get("/flat")
def list_departments_flat(db: Session = Depends(get_db)):
    """获取扁平部门列表"""
    depts = department_service.get_all_departments(db)
    return [{"id": d.id, "name": d.name, "code": d.code, "parent_id": d.parent_id, "sort_order": d.sort_order} for d in depts]


@router.post("/")
def create_department(data: DeptCreate, db: Session = Depends(get_db)):
    return department_service.create_department(db, data.name, data.code, data.parent_id, data.sort_order)


@router.put("/{dept_id}")
def update_department(dept_id: int, data: DeptUpdate, db: Session = Depends(get_db)):
    dept = department_service.update_department(db, dept_id, **data.dict(exclude_none=True))
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept


@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    try:
        ok = department_service.delete_department(db, dept_id)
        if not ok:
            raise HTTPException(status_code=404, detail="部门不存在")
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
