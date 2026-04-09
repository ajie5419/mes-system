import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.automation_rule import AutomationRule, AutomationExecutionLog
from datetime import datetime, date

logger = logging.getLogger(__name__)


def get_rules(db: Session, enabled_only: bool = False) -> List[AutomationRule]:
    q = db.query(AutomationRule)
    if enabled_only:
        q = q.filter(AutomationRule.is_enabled == True)
    return q.order_by(AutomationRule.id).all()


def get_rule(db: Session, rule_id: int) -> Optional[AutomationRule]:
    return db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()


def create_rule(db: Session, data: dict) -> AutomationRule:
    rule = AutomationRule(**data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: int, data: dict) -> Optional[AutomationRule]:
    rule = get_rule(db, rule_id)
    if not rule:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(rule, k, v)
    rule.updated_at = datetime.now()
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int) -> bool:
    rule = get_rule(db, rule_id)
    if not rule:
        return False
    db.delete(rule)
    db.commit()
    return True


def toggle_rule(db: Session, rule_id: int) -> Optional[AutomationRule]:
    rule = get_rule(db, rule_id)
    if not rule:
        return None
    rule.is_enabled = not rule.is_enabled
    rule.updated_at = datetime.now()
    db.commit()
    db.refresh(rule)
    return rule


def _log_execution(db: Session, rule: AutomationRule, event_type: str, event_data: dict,
                   status: str = "success", error: str = None):
    log = AutomationExecutionLog(
        rule_id=rule.id, rule_name=rule.name,
        event_type=event_type, event_data=event_data,
        action_type=rule.action_type, action_params=rule.action_params,
        execution_status=status, error_message=error,
    )
    db.add(log)
    db.commit()


def _condition_match(trigger_condition: dict, event_data: dict) -> bool:
    """检查事件数据是否匹配触发条件"""
    for key, value in trigger_condition.items():
        if key not in event_data:
            return False
        if isinstance(value, list):
            if event_data[key] not in value:
                return False
        elif isinstance(value, dict):
            # Support operators: eq, ne, gt, lt, gte, lte, in, contains
            ops = value
            ev = event_data[key]
            if "eq" in ops and ev != ops["eq"]:
                return False
            if "ne" in ops and ev == ops["ne"]:
                return False
            if "gt" in ops and not (ev > ops["gt"]):
                return False
            if "lt" in ops and not (ev < ops["lt"]):
                return False
            if "gte" in ops and not (ev >= ops["gte"]):
                return False
            if "lte" in ops and not (ev <= ops["lte"]):
                return False
            if "in" in ops and ev not in ops["in"]:
                return False
        elif event_data[key] != value:
            return False
    return True


def _execute_action(db: Session, rule: AutomationRule, event_data: dict):
    """执行规则动作"""
    from services.notification_service import create_notification

    params = rule.action_params or {}
    action = rule.action_type

    if action == "send_notification":
        title = params.get("title", f"自动化通知: {rule.name}")
        content = params.get("content", "").format(**event_data)
        ntype = params.get("type", "info")
        target_roles = params.get("target_roles", [])

        # Find users by role
        from models.user import User
        q = db.query(User).filter(User.is_active == True)
        if target_roles:
            q = q.filter(User.role.in_(target_roles))
        users = q.all()
        for u in users:
            resource_type = params.get("resource_type", "work_order")
            resource_id = params.get("resource_id") or event_data.get("wo_id")
            create_notification(db, u.id, title, content, ntype, resource_type, resource_id)

    elif action == "change_status":
        wo_id = event_data.get("wo_id")
        new_status = params.get("new_status")
        if wo_id and new_status:
            from models.work_order import WorkOrder
            wo = db.query(WorkOrder).get(wo_id)
            if wo:
                wo.status = new_status
                if new_status in ("Blocked",):
                    wo.is_locked = True
                if "health_status" in params:
                    wo.health_status = params["health_status"]
                db.commit()

    elif action == "escalate":
        from services.notification_service import create_notification
        title = params.get("title", f"升级通知: {rule.name}")
        content = params.get("content", "").format(**event_data)
        target_roles = params.get("target_roles", ["Admin", "Manager"])
        from models.user import User
        users = db.query(User).filter(User.is_active == True, User.role.in_(target_roles)).all()
        for u in users:
            create_notification(db, u.id, title, content, "error", "work_order", event_data.get("wo_id"))

    elif action == "create_task":
        from models.department_task import DepartmentTask
        task = DepartmentTask(
            title=params.get("title", f"自动任务: {rule.name}").format(**event_data),
            description=params.get("description", "").format(**event_data),
            department_id=params.get("department_id"),
            status="todo",
            priority=params.get("priority", "high"),
        )
        if task.department_id:
            db.add(task)
            db.commit()


def evaluate_rules(db: Session, event_type: str, event_data: dict):
    """评估并执行所有匹配的自动化规则"""
    rules = get_rules(db, enabled_only=True)
    for rule in rules:
        if rule.trigger_type != event_type:
            continue
        try:
            if not _condition_match(rule.trigger_condition or {}, event_data):
                continue
            _execute_action(db, rule, event_data)
            _log_execution(db, rule, event_type, event_data, "success")
            logger.info(f"自动化规则 '{rule.name}' 执行成功")
        except Exception as e:
            logger.error(f"自动化规则 '{rule.name}' 执行失败: {e}")
            _log_execution(db, rule, event_type, event_data, "failed", str(e))


def get_execution_logs(db: Session, rule_id: int = None, limit: int = 50) -> List[AutomationExecutionLog]:
    q = db.query(AutomationExecutionLog)
    if rule_id:
        q = q.filter(AutomationExecutionLog.rule_id == rule_id)
    return q.order_by(AutomationExecutionLog.id.desc()).limit(limit).all()


def init_default_automation_rules(db: Session):
    """初始化默认自动化规则"""
    existing = db.query(AutomationRule).count()
    if existing > 0:
        return

    defaults = [
        {
            "name": "工单延期2天标黄预警",
            "description": "工单超过计划交付日期2天，自动标黄并通知项目经理",
            "trigger_type": "due_date_approaching",
            "trigger_condition": {"days_overdue": {"gte": 2, "lt": 5}},
            "action_type": "change_status",
            "action_params": {"new_status": "InProgress", "health_status": "yellow"},
            "is_enabled": True,
        },
        {
            "name": "工单延期5天标红升级",
            "description": "工单超过计划交付日期5天，自动标红并升级通知管理层",
            "trigger_type": "due_date_approaching",
            "trigger_condition": {"days_overdue": {"gte": 5}},
            "action_type": "escalate",
            "action_params": {
                "title": "工单严重延期升级: {wo_number}",
                "content": "工单 {wo_number} 已延期{days_overdue}天，请立即处理",
                "target_roles": ["Admin", "Manager"],
                "new_status": "InProgress",
                "health_status": "red",
            },
            "is_enabled": True,
        },
        {
            "name": "严重异常立即通知管理层",
            "description": "严重级别(critical)异常上报时，立即通知管理层并创建应急任务",
            "trigger_type": "exception_created",
            "trigger_condition": {"severity": "critical"},
            "action_type": "escalate",
            "action_params": {
                "title": "严重异常: {exception_type}",
                "content": "工单 {wo_number} 出现严重异常: {description}",
                "target_roles": ["Admin", "Manager"],
            },
            "is_enabled": True,
        },
        {
            "name": "进度连续3天未更新预警",
            "description": "工单进度连续3天未汇报，自动发送漏报预警通知",
            "trigger_type": "progress_stalled",
            "trigger_condition": {"stalled_days": {"gte": 3}},
            "action_type": "send_notification",
            "action_params": {
                "title": "进度漏报预警: {wo_number}",
                "content": "工单 {wo_number} 已连续{stalled_days}天未更新进度，请及时汇报",
                "target_roles": ["Manager", "Technician"],
                "type": "warning",
            },
            "is_enabled": True,
        },
        {
            "name": "工单完成自动通知",
            "description": "工单完成时自动发送通知",
            "trigger_type": "status_change",
            "trigger_condition": {"new_status": "Completed"},
            "action_type": "send_notification",
            "action_params": {
                "title": "工单已完成: {wo_number}",
                "content": "工单 {wo_number} 已完成交付",
                "target_roles": ["Admin", "Manager", "Technician"],
                "type": "success",
            },
            "is_enabled": True,
        },
        {
            "name": "里程碑完成触发下一节点",
            "description": "里程碑完成时自动触发下一个里程碑通知",
            "trigger_type": "status_change",
            "trigger_condition": {"new_status": "Completed"},
            "action_type": "send_notification",
            "action_params": {
                "title": "里程碑节点提醒",
                "content": "工单 {wo_number} 当前阶段已完成，请开始下一阶段工作",
                "target_roles": ["Technician", "Manager"],
                "type": "info",
            },
            "is_enabled": True,
        },
    ]
    for d in defaults:
        rule = AutomationRule(**d)
        db.add(rule)
    db.commit()
    logger.info(f"已初始化 {len(defaults)} 条默认自动化规则")
