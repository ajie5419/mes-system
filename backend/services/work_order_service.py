from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from models.work_order import WorkOrder
from models.milestone import Milestone
from schemas.work_order import WorkOrderCreate, WorkOrderUpdate


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
        # 若未指定，按默认模板初始化
        default_nodes = [
            "项目生效", "制定工单", "项目计划", "技术出图",
            "图纸下发", "采购计划", "采购评审", "下达订单",
            "工艺编制", "下发生产", "任务分配", "生产制作",
            "进度录入", "偏差核对", "成品入库", "成品发货", "项目关闭",
        ]
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


def delete_work_order(db: Session, wo_id: int) -> bool:
    wo = get_work_order(db, wo_id)
    if not wo:
        return False
    db.delete(wo)
    db.commit()
    return True


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
