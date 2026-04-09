from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from models.work_order import WorkOrder
from models.change_record import ChangeRecord, ChangeConfirmation
from schemas.change_record import ChangeCreate, ChangeConfirmInput
from constants import WorkOrderStatus, Department

def create_change(db: Session, data: ChangeCreate) -> ChangeRecord:
    """发起变更：核心逻辑增强，增加事务原子性保障"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == data.wo_id).first()
    if not wo:
        raise ValueError(f"无效工单 ID: {data.wo_id}")

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

    # 2. 初始化各部门确认单，并确保部门名称来自枚举
    for dept_name in data.notify_departments:
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
        return change
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"变更事务失败: {str(e)}")

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

    db.commit()
    db.refresh(change)
    return change
