from sqlalchemy.orm import Session
from models.role import Role


def init_default_roles(db: Session):
    """初始化默认角色"""
    defaults = [
        ("管理员", "Admin", "系统管理员，拥有全部权限", True, 100),
        ("经理", "Manager", "部门经理，拥有大部分业务权限", True, 50),
        ("工人", "Worker", "一线操作人员，拥有基础操作权限", True, 10),
    ]
    for name, code, desc, is_sys, level in defaults:
        existing = db.query(Role).filter(Role.code == code).first()
        if not existing:
            db.add(Role(name=name, code=code, description=desc, is_system=is_sys, level=level))
    db.commit()


def get_all_roles(db: Session):
    return db.query(Role).order_by(Role.level.desc()).all()


def get_role_by_code(db: Session, code: str):
    return db.query(Role).filter(Role.code == code).first()
