from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from models.work_order import WorkOrder
from models.change_record import ChangeRecord, ChangeConfirmation
from schemas.change_record import ChangeCreate, ChangeConfirmInput
from constants import WorkOrderStatus, Department
import json


def _get_default_notify_departments(db: Session) -> List[str]:
    """从系统配置获取默认通知部门，fallback到数据库部门表，最后用常量"""
    try:
        from services.config_service import get_config
        val = get_config(db, "notify_departments")
        if val:
            depts = json.loads(val)
            if isinstance(depts, list):
                return depts
    except Exception:
        pass
    # fallback to department table
    try:
        from services.department_service import get_department_names
        return get_department_names(db)
    except Exception:
        pass
    # fallback to constants
    return [d.value for d in Department]


def create_change(db: Session, data: ChangeCreate) -> ChangeRecord:
    """发起变更：核心逻辑增强，增加事务原子性保障"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == data.wo_id).first()
    if not wo:
        raise ValueError(f"无效工单 ID: {data.wo_id}")

    notify_depts = data.notify_departments or _get_default_notify_departments(db)

    # 1. 创建变更主记录
    change = ChangeRecord(
        wo_id=data.wo_id,
        change_type=data.change_type,
        description=data.description,
        initiated_by=data.initiated_by,
        status="Pending"
    )
    db.add(change)
    db.flush()

    # 2. 初始化各部门确认单
    for dept_name in notify_depts:
        confirmation = ChangeConfirmation(
            change_id=change.id,
            department=dept_name,
            confirmed=False
        )
        db.add(confirmation)

    # 3. 锁定工单：状态流转严谨化
    wo.is_locked = True
    wo.status = WorkOrderStatus.BLOCKED.value

    try:
        db.commit()
        db.refresh(change)
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"变更事务失败: {str(e)}")

    # 变更发起通知：通知相关部门
    try:
        from services.notification_service import create_batch_notifications
        from models.user import User
        for dept in notify_depts:
            dept_users = db.query(User).filter(User.department == dept, User.is_active == True).all()
            if dept_users:
                create_batch_notifications(db, [u.id for u in dept_users],
                    title=f"变更待确认: {change.change_type}",
                    content=f"工单ID: {data.wo_id}，描述: {data.description}",
                    type="warning", resource_type="change", resource_id=change.id)
    except Exception:
        pass

    return change

def get_changes(db: Session, wo_id: int = None) -> List[ChangeRecord]:
    """获取变更记录列表"""
    q = db.query(ChangeRecord)
    if wo_id:
        q = q.filter(ChangeRecord.wo_id == wo_id)
    return q.order_by(ChangeRecord.created_at.desc()).all()


def confirm_change(db: Session, change_id: int, data: ChangeConfirmInput) -> ChangeRecord:
    """部门负责人确认变更：增加幂等性检查"""
    change = db.query(ChangeRecord).filter(ChangeRecord.id == change_id).first()
    if not change or change.status == "Confirmed":
        return change

    confirmation = db.query(ChangeConfirmation).filter(
        ChangeConfirmation.change_id == change_id,
        ChangeConfirmation.department == data.department
    ).first()

    if not confirmation or confirmation.confirmed:
        return change

    confirmation.confirmed = True
    confirmation.confirmed_at = datetime.now()
    confirmation.confirmed_by = data.confirmed_by

    # 检查是否达成解锁条件
    all_done = all(c.confirmed for c in change.confirmations)
    if all_done:
        change.status = "Confirmed"
        wo = db.query(WorkOrder).filter(WorkOrder.id == change.wo_id).first()
        if wo:
            wo.is_locked = False
            wo.status = WorkOrderStatus.IN_PROGRESS.value

        # 变更全部确认通知
        try:
            from services.notification_service import create_batch_notifications
            from models.user import User
            initiator = db.query(User).filter(User.id == change.initiated_by).first()
            notify_ids = set()
            if initiator:
                notify_ids.add(initiator.id)
            for dept_name in data.department if hasattr(data, 'department') else []:
                dept_users = db.query(User).filter(User.department == dept_name, User.is_active == True).all()
                for u in dept_users:
                    notify_ids.add(u.id)
            if notify_ids:
                create_batch_notifications(db, list(notify_ids),
                    title=f"变更已确认: {change.change_type}",
                    content=f"工单ID: {change.wo_id}，所有部门已确认，工单已解锁",
                    type="success", resource_type="change", resource_id=change.id)
        except Exception:
            pass

    db.commit()
    db.refresh(change)
    return change
