from typing import List, Optional
from sqlalchemy.orm import Session
from models.work_order_template import WorkOrderTemplate, MilestoneTemplate
from models.milestone import Milestone
from models.work_order import WorkOrder


def init_default_template(db: Session):
    """初始化默认17节点工单模板"""
    existing = db.query(WorkOrderTemplate).filter(WorkOrderTemplate.is_default == True).first()
    if existing:
        return existing

    template = WorkOrderTemplate(
        name="标准制造工单模板",
        description="包含17个标准里程碑节点的默认制造工单模板",
        industry_type="通用制造",
        is_default=True,
    )
    db.add(template)
    db.flush()

    nodes = [
        ("项目生效", "审批", None, True),
        ("制定工单", "执行", None, True),
        ("项目计划", "审批", None, True),
        ("技术出图", "执行", None, True),
        ("图纸下发", "交付", None, True),
        ("采购计划", "审批", None, True),
        ("采购评审", "检验", None, True),
        ("下达订单", "执行", None, True),
        ("工艺编制", "执行", None, True),
        ("下发生产", "交付", None, True),
        ("任务分配", "执行", None, True),
        ("生产制作", "执行", None, True),
        ("进度录入", "执行", None, True),
        ("偏差核对", "检验", None, True),
        ("成品入库", "交付", None, True),
        ("成品发货", "交付", None, True),
        ("项目关闭", "审批", None, True),
    ]
    for idx, (name, ntype, duration, required) in enumerate(nodes):
        db.add(MilestoneTemplate(
            template_id=template.id,
            node_name=name,
            node_type=ntype,
            default_duration_days=duration,
            sort_order=idx,
            is_required=required,
        ))
    db.commit()
    return template


def get_template(db: Session, template_id: int) -> Optional[WorkOrderTemplate]:
    return db.query(WorkOrderTemplate).get(template_id)


def get_all_templates(db: Session) -> List[WorkOrderTemplate]:
    return db.query(WorkOrderTemplate).order_by(WorkOrderTemplate.id).all()


def get_template_nodes(db: Session, template_id: int) -> List[str]:
    """获取模板的节点名称列表"""
    nodes = db.query(MilestoneTemplate).filter(
        MilestoneTemplate.template_id == template_id
    ).order_by(MilestoneTemplate.sort_order).all()
    return [n.node_name for n in nodes]


def get_default_template_nodes(db: Session) -> List[str]:
    """获取默认模板的节点名称（向后兼容）"""
    default_tpl = db.query(WorkOrderTemplate).filter(WorkOrderTemplate.is_default == True).first()
    if default_tpl:
        return get_template_nodes(db, default_tpl.id)
    # fallback
    return [
        "项目生效", "制定工单", "项目计划", "技术出图",
        "图纸下发", "采购计划", "采购评审", "下达订单",
        "工艺编制", "下发生产", "任务分配", "生产制作",
        "进度录入", "偏差核对", "成品入库", "成品发货", "项目关闭",
    ]


def create_work_order_milestones_from_template(db: Session, wo_id: int, template_id: int = None, planned_end_date=None):
    """根据模板为工单创建里程碑"""
    if template_id:
        nodes = db.query(MilestoneTemplate).filter(
            MilestoneTemplate.template_id == template_id
        ).order_by(MilestoneTemplate.sort_order).all()
    else:
        # 使用默认模板
        default_tpl = db.query(WorkOrderTemplate).filter(WorkOrderTemplate.is_default == True).first()
        if default_tpl:
            nodes = db.query(MilestoneTemplate).filter(
                MilestoneTemplate.template_id == default_tpl.id
            ).order_by(MilestoneTemplate.sort_order).all()
        else:
            return  # no template, caller handles fallback

    for node in nodes:
        milestone = Milestone(
            wo_id=wo_id,
            node_name=node.node_name,
            sort_order=node.sort_order,
            planned_end_date=planned_end_date,
        )
        db.add(milestone)
