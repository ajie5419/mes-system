import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from models.work_order import WorkOrder
from models.status_transition import StatusTransition
from models.user import User
from models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)

# ── 状态流转规则定义 ──
TRANSITION_RULES: Dict[str, Dict[str, dict]] = {
    "Draft": {
        "PendingReview": {
            "require_permission": "work_orders:update",
            "label": "提交审核",
            "pre_check": lambda wo: bool(wo.project_name),
            "pre_check_msg": "工单信息不完整，无法提交审核",
        },
    },
    "PendingReview": {
        "Approved": {
            "require_permission": "approvals:approve",
            "label": "批准",
        },
        "Rejected": {
            "require_permission": "approvals:approve",
            "label": "驳回",
        },
    },
    "Approved": {
        "InProgress": {
            "require_permission": "work_orders:update",
            "label": "开始执行",
        },
    },
    "InProgress": {
        "Blocked": {
            "require_permission": "changes:create",
            "label": "阻塞",
        },
        "OnHold": {
            "require_permission": "work_orders:update",
            "label": "暂停",
        },
        "Completed": {
            "require_permission": "work_orders:update",
            "label": "完成",
            "pre_check": lambda wo: wo.total_progress >= 100 if wo.total_progress else True,
            "pre_check_msg": "进度未达100%，无法完成",
        },
    },
    "Blocked": {
        "InProgress": {
            "require_permission": "changes:confirm",
            "label": "恢复（变更确认）",
        },
    },
    "OnHold": {
        "InProgress": {
            "require_permission": "work_orders:update",
            "label": "恢复",
        },
    },
    "Completed": {
        "Closed": {
            "require_permission": "work_orders:update",
            "label": "关闭",
        },
    },
    "Rejected": {
        "Draft": {
            "require_permission": "work_orders:update",
            "label": "重新编辑",
        },
    },
    # Legacy statuses (backward compat)
    "Backlog": {
        "InProgress": {"require_permission": "work_orders:update", "label": "开始执行"},
        "Archived": {"require_permission": "work_orders:delete", "label": "直接归档"},
    },
    "Archived": {},
}

ALL_STATUSES = list(TRANSITION_RULES.keys())
TERMINAL_STATUSES = {"Archived", "Closed"}

# Status labels for UI
STATUS_LABELS = {
    "Draft": "草稿", "PendingReview": "待审核", "Approved": "已批准",
    "InProgress": "进行中", "Blocked": "阻塞", "OnHold": "暂停",
    "Completed": "已完成", "Closed": "已关闭", "Rejected": "已驳回",
    "Backlog": "待排产", "Archived": "已归档",
}

STATUS_COLORS = {
    "Draft": "info", "PendingReview": "warning", "Approved": "success",
    "InProgress": "primary", "Blocked": "danger", "OnHold": "warning",
    "Completed": "success", "Closed": "info", "Rejected": "danger",
    "Backlog": "info", "Archived": "info",
}


def get_available_transitions(current_status: str) -> List[Tuple[str, str]]:
    rules = TRANSITION_RULES.get(current_status, {})
    return [(target, rule["label"]) for target, rule in rules.items()]


def is_valid_transition(current_status: str, target_status: str) -> bool:
    return target_status in TRANSITION_RULES.get(current_status, {})


def transition_order_status(
    db: Session, wo_id: int, target_status: str, user_id: int, reason: str = ""
) -> dict:
    """执行工单状态流转，返回详细结果"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        return {"success": False, "new_status": None, "message": f"工单不存在: {wo_id}", "actions_performed": []}

    if wo.status in TERMINAL_STATUSES:
        return {"success": False, "new_status": wo.status, "message": f"工单已处于终态 '{wo.status}'", "actions_performed": []}

    if not is_valid_transition(wo.status, target_status):
        available = get_available_transitions(wo.status)
        available_str = ", ".join([f"{t[0]}({t[1]})" for t in available])
        return {
            "success": False, "new_status": wo.status,
            "message": f"非法状态流转: '{wo.status}' → '{target_status}'。允许: {available_str or '无'}",
            "actions_performed": [],
        }

    rule = TRANSITION_RULES[wo.status][target_status]

    # 前置条件检查
    pre_check = rule.get("pre_check")
    if pre_check and not pre_check(wo):
        msg = rule.get("pre_check_msg", "前置条件不满足")
        return {"success": False, "new_status": wo.status, "message": msg, "actions_performed": []}

    old_status = wo.status
    wo.status = target_status
    actions_performed = []

    # 状态相关自动动作
    if target_status == "Blocked":
        wo.is_locked = True
        actions_performed.append("自动锁定工单")
    if old_status == "Blocked" and target_status == "InProgress":
        wo.is_locked = False
        actions_performed.append("自动解锁工单")
    if target_status == "Completed":
        from datetime import date
        wo.actual_delivery_date = date.today()
        actions_performed.append("自动设置实际交付日期")

    db.commit()
    db.refresh(wo)

    # 记录状态变更历史
    try:
        user = db.query(User).get(user_id)
        username = user.username if user else f"user_{user_id}"
        transition = StatusTransition(
            wo_id=wo_id, from_status=old_status, to_status=target_status,
            transitioned_by=user_id, reason=reason,
        )
        db.add(transition)

        # 审计日志
        detail = f"{old_status} → {target_status}"
        if reason:
            detail += f" | 原因: {reason}"
        log = AuditLog(
            action="status_transition", resource_type="work_order",
            resource_id=wo_id, detail=detail, operator=username,
        )
        db.add(log)
        db.commit()
        actions_performed.append("记录状态变更历史")
    except Exception as e:
        logger.error(f"记录状态变更失败: {e}")

    # 触发通知
    try:
        from services.notification_service import create_notification
        notif_map = {
            "PendingReview": ("工单待审核", f"工单 {wo.wo_number} 已提交审核", "info"),
            "Approved": ("工单已批准", f"工单 {wo.wo_number} 已批准通过", "success"),
            "Rejected": ("工单已驳回", f"工单 {wo.wo_number} 已被驳回: {reason or '无原因'}", "error"),
            "Completed": ("工单已完成", f"工单 {wo.wo_number} 已完成", "success"),
            "Closed": ("工单已关闭", f"工单 {wo.wo_number} 已关闭", "info"),
            "Blocked": ("工单阻塞", f"工单 {wo.wo_number} 已进入阻塞状态", "warning"),
            "OnHold": ("工单暂停", f"工单 {wo.wo_number} 已暂停", "warning"),
        }
        if target_status in notif_map:
            title, content, ntype = notif_map[target_status]
            # 通知相关管理人员
            notify_users = []
            if wo.technical_manager_id:
                notify_users.append(wo.technical_manager_id)
            if wo.production_manager_id:
                notify_users.append(wo.production_manager_id)
            for uid in notify_users:
                create_notification(db, uid, title, content, ntype, "work_order", wo_id)
            actions_performed.append(f"已发送通知给{len(notify_users)}位相关人员")
    except Exception as e:
        logger.error(f"触发通知失败: {e}")

    # 触发自动化规则
    try:
        from services.automation_service import evaluate_rules
        evaluate_rules(db, "status_change", {
            "wo_id": wo_id, "wo_number": wo.wo_number,
            "old_status": old_status, "new_status": target_status,
            "user_id": user_id,
        })
        actions_performed.append("已评估自动化规则")
    except Exception as e:
        logger.error(f"自动化规则评估失败: {e}")

    return {
        "success": True, "new_status": target_status,
        "message": f"状态已从 '{old_status}' 变更为 '{target_status}'",
        "actions_performed": actions_performed,
    }
