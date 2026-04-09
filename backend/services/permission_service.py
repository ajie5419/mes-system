from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.permission import Permission, RolePermission

# ── Default permissions by module ──
DEFAULT_PERMISSIONS = {
    "work_orders": [
        ("work_orders:read", "查看工单"),
        ("work_orders:create", "创建工单"),
        ("work_orders:update", "编辑工单"),
        ("work_orders:delete", "删除工单"),
    ],
    "users": [
        ("users:read", "查看用户"),
        ("users:create", "创建用户"),
        ("users:update", "编辑用户"),
    ],
    "changes": [
        ("changes:read", "查看变更"),
        ("changes:create", "发起变更"),
        ("changes:confirm", "确认变更"),
    ],
    "progress": [
        ("progress:read", "查看进度"),
        ("progress:report", "汇报进度"),
    ],
    "extra": [
        ("extra:read", "查看扩展模块"),
        ("extra:create", "管理扩展模块"),
    ],
    "dashboard": [
        ("dashboard:read", "查看看板"),
    ],
    "audit": [
        ("audit:read", "查看审计日志"),
    ],
}

# ── Role defaults ──
ROLE_PERMISSIONS = {
    "Admin": "all",
    "Manager": [
        # read all
        "work_orders:read", "users:read", "changes:read", "progress:read",
        "extra:read", "dashboard:read", "audit:read",
        # write
        "work_orders:create", "work_orders:update",
        "users:create", "users:update",
        "changes:create", "changes:confirm",
        "progress:report",
        "extra:create",
    ],
    "Worker": [
        "work_orders:read",
        "progress:read", "progress:report",
        "extra:read",
        "dashboard:read",
    ],
}

ALL_PERMISSION_CODES = [code for perms in DEFAULT_PERMISSIONS.values() for code, _ in perms]


def init_default_permissions(db: Session):
    """Create permission records if not exist."""
    for module, perms in DEFAULT_PERMISSIONS.items():
        for code, name in perms:
            existing = db.query(Permission).filter_by(code=code).first()
            if not existing:
                db.add(Permission(code=code, name=name, module=module))
    db.commit()


def init_role_permissions(db: Session):
    """Assign default permissions to roles."""
    for role, perm_list in ROLE_PERMISSIONS.items():
        codes = perm_list if perm_list != "all" else ALL_PERMISSION_CODES
        for code in codes:
            perm = db.query(Permission).filter_by(code=code).first()
            if perm and not db.query(RolePermission).filter_by(role=role, permission_id=perm.id).first():
                db.add(RolePermission(role=role, permission_id=perm.id))
    db.commit()


def get_user_permissions(db: Session, user_role: str) -> List[str]:
    """Get all permission codes for a role."""
    rows = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role == user_role)
        .all()
    )
    return [r.code for r in rows]


def check_permission(db: Session, user_role: str, required: str) -> bool:
    """Check if role has a specific permission."""
    count = (
        db.query(RolePermission)
        .join(Permission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role == user_role, Permission.code == required)
        .count()
    )
    return count > 0


def get_all_permissions(db: Session) -> Dict[str, List[dict]]:
    """Return permissions grouped by module."""
    perms = db.query(Permission).filter_by(is_active=True).order_by(Permission.module, Permission.id).all()
    groups: Dict[str, List[dict]] = {}
    for p in perms:
        groups.setdefault(p.module, []).append({"id": p.id, "code": p.code, "name": p.name})
    return groups


def get_role_permissions(db: Session) -> Dict[str, List[str]]:
    """Return role -> [permission_codes] mapping."""
    result = {}
    for rp in db.query(RolePermission).all():
        perm = db.query(Permission).get(rp.permission_id)
        if perm:
            result.setdefault(rp.role, []).append(perm.code)
    return result


def update_role_permissions(db: Session, role: str, permission_codes: List[str]):
    """Replace all permissions for a role."""
    db.query(RolePermission).filter_by(role=role).delete()
    for code in permission_codes:
        perm = db.query(Permission).filter_by(code=code).first()
        if perm:
            db.add(RolePermission(role=role, permission_id=perm.id))
    db.commit()
