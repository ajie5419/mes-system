from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from models.work_order import WorkOrder
from models.milestone import Milestone
from schemas.work_order import WorkOrderCreate, WorkOrderUpdate, MilestoneCreate
from services.template_service import get_default_template_nodes, create_work_order_milestones_from_template


def generate_wo_number(db: Session) -> str:
    """自动生成工单号: WO-YYYYMMDD-NNN"""
    today_str = date.today().strftime("%Y%m%d")
    prefix = f"WO-{today_str}-"

    last_wo = (
        db.query(WorkOrder)
        .filter(WorkOrder.wo_number.like(f"{prefix}%"))
        .order_by(WorkOrder.wo_number.desc())
        .first()
    )

    if last_wo:
        last_seq = int(last_wo.wo_number.split("-")[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f"{prefix}{new_seq:03d}"


def create_work_order(db: Session, data: WorkOrderCreate) -> WorkOrder:
    """创建工单并初始化里程碑节点"""
    wo_number = generate_wo_number(db)

    wo = WorkOrder(
        wo_number=wo_number,
        project_name=data.project_name,
        customer_name=data.customer_name,
        priority=data.priority,
        planned_delivery_date=data.planned_delivery_date,
        technical_manager_id=data.technical_manager_id,
        production_manager_id=data.production_manager_id,
        status="Backlog",
    )
    db.add(wo)
    db.flush()  # 获取 wo.id

    # 初始化里程碑
    if data.milestones:
        for idx, m in enumerate(data.milestones):
            milestone = Milestone(
                wo_id=wo.id,
                node_name=m.node_name,
                sort_order=m.sort_order or idx,
                planned_start_date=m.planned_start_date,
                planned_end_date=m.planned_end_date,
            )
            db.add(milestone)
    else:
        # 若未指定，按默认模板初始化（优先从数据库模板获取）
        try:
            create_work_order_milestones_from_template(db, wo.id, planned_end_date=data.planned_delivery_date)
            created_from_template = db.query(Milestone).filter(Milestone.wo_id == wo.id).count() > 0
        except Exception:
            created_from_template = False

        if not created_from_template:
            # fallback: 硬编码默认节点
            default_nodes = get_default_template_nodes(db)
            for idx, name in enumerate(default_nodes):
                milestone = Milestone(
                    wo_id=wo.id,
                    node_name=name,
                    sort_order=idx,
                    planned_end_date=data.planned_delivery_date,
                )
                db.add(milestone)

    db.commit()
    db.refresh(wo)

    # 工单创建通知
    try:
        from services.notification_service import create_notification, create_batch_notifications
        from models.user import User
        admins = db.query(User).filter(User.role == "Admin", User.is_active == True).all()
        if admins:
            admin_ids = [a.id for a in admins]
            create_batch_notifications(db, admin_ids,
                title=f"新工单创建: {wo.wo_number}",
                content=f"项目: {wo.project_name}，客户: {wo.customer_name}",
                type="info", resource_type="work_order", resource_id=wo.id)
    except Exception:
        pass

    return wo


def get_work_order(db: Session, wo_id: int) -> Optional[WorkOrder]:
    return db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()


def get_work_orders(
    db: Session,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    is_delayed: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(WorkOrder)

    if status:
        query = query.filter(WorkOrder.status == status)
    if keyword:
        query = query.filter(
            (WorkOrder.project_name.contains(keyword))
            | (WorkOrder.wo_number.contains(keyword))
            | (WorkOrder.customer_name.contains(keyword))
        )
    if is_delayed is True:
        query = query.filter(WorkOrder.health_status == "RED")

    total = query.count()
    items = (
        query.order_by(WorkOrder.priority.asc(), WorkOrder.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def update_work_order(db: Session, wo_id: int, data: WorkOrderUpdate) -> Optional[WorkOrder]:
    wo = get_work_order(db, wo_id)
    if not wo:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wo, key, value)

    wo.updated_at = datetime.now()
    db.commit()
    db.refresh(wo)
    return wo


def create_milestone(db: Session, wo_id: int, data: MilestoneCreate) -> WorkOrder:
    wo = get_work_order(db, wo_id)
    if not wo:
        raise ValueError(f"工单 ID {wo_id} 不存在")

    if data.planned_start_date and data.planned_start_date > data.planned_end_date:
        raise ValueError("计划开始日期不能晚于计划结束日期")

    if data.sort_order is None:
        max_sort_order = db.query(func.max(Milestone.sort_order)).filter(Milestone.wo_id == wo_id).scalar()
        sort_order = (max_sort_order or 0) + 1
    else:
        sort_order = data.sort_order

    milestone = Milestone(
        wo_id=wo_id,
        node_name=data.node_name,
        planned_start_date=data.planned_start_date,
        planned_end_date=data.planned_end_date,
        sort_order=sort_order,
    )
    db.add(milestone)

    wo.updated_at = datetime.now()
    db.commit()
    recalculate_wo_health(db, wo_id)
    db.refresh(wo)
    return wo


def delete_work_order(db: Session, wo_id: int) -> bool:
    wo = get_work_order(db, wo_id)
    if not wo:
        return False
    db.delete(wo)
    db.commit()
    return True


def get_gantt_data(db: Session, wo_id: Optional[int] = None) -> List:
    """获取甘特图数据，含里程碑实际进度与计划对比"""
    if wo_id:
        work_orders = [get_work_order(db, wo_id)]
        work_orders = [wo for wo in work_orders if wo is not None]
    else:
        work_orders = (
            db.query(WorkOrder)
            .filter(WorkOrder.status.in_(["Backlog", "InProgress", "Blocked"]))
            .order_by(WorkOrder.priority.asc(), WorkOrder.created_at.desc())
            .all()
        )

    result = []
    for wo in work_orders:
        milestones = (
            db.query(Milestone)
            .filter(Milestone.wo_id == wo.id)
            .order_by(Milestone.sort_order.asc(), Milestone.planned_end_date.asc())
            .all()
        )
        result.append({
            "id": wo.id,
            "wo_number": wo.wo_number,
            "project_name": wo.project_name,
            "status": wo.status,
            "total_progress": wo.total_progress,
            "planned_delivery_date": wo.planned_delivery_date,
            "milestones": milestones,
        })
    return result


def recalculate_wo_health(db: Session, wo_id: int):
    """重新计算工单的总进度与健康状态"""
    wo = get_work_order(db, wo_id)
    if not wo:
        return

    milestones = db.query(Milestone).filter(Milestone.wo_id == wo_id).all()
    if not milestones:
        return

    today = date.today()
    total_rate = 0.0
    worst_status = "GREEN"

    for m in milestones:
        total_rate += m.completion_rate

        # 计算偏差天数（仅对未完成的节点）
        if m.status != "Completed" and m.planned_end_date:
            delta = (today - m.planned_end_date).days
            m.deviation_days = max(delta, 0)

            if delta > 5:
                worst_status = "RED"
            elif delta > 2 and worst_status != "RED":
                worst_status = "YELLOW"
        elif m.status == "Completed":
            m.deviation_days = 0

    wo.total_progress = round(total_rate / len(milestones), 2)
    wo.health_status = worst_status

    db.commit()


def assign_department(db: Session, wo_id: int, department_id: int, user_ids: list, role_in_wo: str):
    """给工单分配部门人员"""
    wo = get_work_order(db, wo_id)
    if not wo:
        return None
    from models.work_order_assignee import WorkOrderAssignee
    for uid in user_ids:
        existing = db.query(WorkOrderAssignee).filter(
            WorkOrderAssignee.wo_id == wo_id,
            WorkOrderAssignee.user_id == uid,
            WorkOrderAssignee.department_id == department_id,
        ).first()
        if not existing:
            assignee = WorkOrderAssignee(wo_id=wo_id, user_id=uid, department_id=department_id, role_in_wo=role_in_wo)
            db.add(assignee)
    db.commit()
    return True


def get_assignees(db: Session, wo_id: int):
    """获取工单所有协作人员"""
    from models.work_order_assignee import WorkOrderAssignee
    rows = db.query(WorkOrderAssignee).filter(WorkOrderAssignee.wo_id == wo_id).all()
    result = []
    for r in rows:
        item = {
            "id": r.id, "wo_id": r.wo_id, "user_id": r.user_id,
            "department_id": r.department_id, "role_in_wo": r.role_in_wo,
            "assigned_at": r.assigned_at,
            "user_name": r.user.display_name if r.user else None,
            "department_name": r.department.name if r.department else None,
        }
        result.append(item)
    return result
