from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models.department import Department


def get_department_tree(db: Session) -> List[Dict]:
    """获取部门树形结构"""
    all_depts = db.query(Department).filter(Department.is_active == True).order_by(Department.sort_order).all()
    dept_map: Dict[int, dict] = {}
    for d in all_depts:
        dept_map[d.id] = {"id": d.id, "name": d.name, "code": d.code, "children": [], "sort_order": d.sort_order}
    root: List[Dict] = []
    for d in all_depts:
        node = dept_map[d.id]
        if d.parent_id and d.parent_id in dept_map:
            dept_map[d.parent_id]["children"].append(node)
        else:
            root.append(node)
    return root


def get_all_departments(db: Session) -> List[Department]:
    return db.query(Department).filter(Department.is_active == True).order_by(Department.sort_order).all()


def get_department_names(db: Session) -> List[str]:
    """获取所有部门名称列表"""
    depts = get_all_departments(db)
    return [d.name for d in depts]


def create_department(db: Session, name: str, code: str, parent_id: int = None, sort_order: int = 0) -> Department:
    dept = Department(name=name, code=code, parent_id=parent_id, sort_order=sort_order)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def update_department(db: Session, dept_id: int, **kwargs) -> Optional[Department]:
    dept = db.query(Department).get(dept_id)
    if not dept:
        return None
    for k, v in kwargs.items():
        if hasattr(dept, k) and v is not None:
            setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


def delete_department(db: Session, dept_id: int) -> bool:
    dept = db.query(Department).get(dept_id)
    if not dept:
        return False
    # 检查是否有子部门
    children = db.query(Department).filter(Department.parent_id == dept_id).count()
    if children > 0:
        raise ValueError("该部门存在子部门，无法删除")
    db.delete(dept)
    db.commit()
    return True


def init_default_departments(db: Session):
    """初始化默认部门"""
    defaults = [
        ("技术部", "TECH", 1),
        ("工艺部", "PROCESS", 2),
        ("采购部", "PURCH", 3),
        ("生产部", "PRODUCTION", 4),
        ("项目管理部", "PROJECT", 5),
        ("质量部", "QUALITY", 6),
        ("仓储部", "WAREHOUSE", 7),
        ("行政部", "ADMIN", 8),
    ]
    for name, code, order in defaults:
        existing = db.query(Department).filter(Department.code == code).first()
        if not existing:
            db.add(Department(name=name, code=code, sort_order=order))
    db.commit()
