import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.work_order import WorkOrder
from models.status_transition import StatusTransition
from models.progress import ProgressReport
from models.comment import Comment
from models.change_record import ChangeRecord
from models.approval import ApprovalInstance, ApprovalStep
from models.exception import Exception as MESException
from models.user import User
from models.audit_log import AuditLog

logger = logging.getLogger(__name__)

# Timeline event type config: icon, color
TIMELINE_ICONS = {
    "status_change": ("el-icon-refresh", "#1890ff"),
    "progress_report": ("el-icon-data-line", "#52c41a"),
    "comment": ("el-icon-chat-dot-round", "#722ed1"),
    "change_record": ("el-icon-edit", "#faad14"),
    "approval": ("el-icon-circle-check", "#1890ff"),
    "exception": ("el-icon-warning", "#ff4d4f"),
    "audit": ("el-icon-document", "#999"),
}


def get_work_order_timeline(db: Session, wo_id: int) -> List[dict]:
    """获取工单完整时间线，按时间倒序"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        return []

    events = []

    # 1. 状态变更
    transitions = db.query(StatusTransition).filter(StatusTransition.wo_id == wo_id).all()
    for t in transitions:
        user = db.query(User).get(t.transitioned_by)
        events.append({
            "timestamp": t.created_at.isoformat() if t.created_at else None,
            "type": "status_change",
            "user": user.display_name if user else "未知",
            "user_id": t.transitioned_by,
            "action": "状态变更",
            "detail": f"{t.from_status} → {t.to_status}" + (f" ({t.reason})" if t.reason else ""),
        })

    # 2. 进度汇报
    reports = db.query(ProgressReport).filter(ProgressReport.wo_id == wo_id).all()
    for r in reports:
        user = db.query(User).get(r.reported_by) if r.reported_by else None
        events.append({
            "timestamp": r.created_at.isoformat() if r.created_at else None,
            "type": "progress_report",
            "user": user.display_name if user else (r.team_name or "系统"),
            "user_id": r.reported_by,
            "action": "进度汇报",
            "detail": f"完成率: {r.completion_rate}%" + (f" - {r.remark}" if r.remark else ""),
        })

    # 3. 评论
    comments = db.query(Comment).filter(
        Comment.resource_type == "work_order", Comment.resource_id == wo_id
    ).all()
    for c in comments:
        user = db.query(User).get(c.user_id)
        events.append({
            "timestamp": c.created_at.isoformat() if c.created_at else None,
            "type": "comment",
            "user": user.display_name if user else "未知",
            "user_id": c.user_id,
            "action": "发表评论" + ("（内部备注）" if c.is_internal else ""),
            "detail": c.content[:200],
        })

    # 4. 变更记录
    changes = db.query(ChangeRecord).filter(ChangeRecord.wo_id == wo_id).all()
    for ch in changes:
        user = db.query(User).get(ch.created_by) if hasattr(ch, 'created_by') else None
        events.append({
            "timestamp": ch.created_at.isoformat() if hasattr(ch, 'created_at') and ch.created_at else None,
            "type": "change_record",
            "user": user.display_name if user else "未知",
            "user_id": getattr(ch, 'created_by', None),
            "action": "变更记录",
            "detail": f"{getattr(ch, 'change_type', '')}: {getattr(ch, 'description', '')[:200]}",
        })

    # 5. 审批记录
    approvals = db.query(ApprovalInstance).filter(ApprovalInstance.wo_id == wo_id).all()
    for inst in approvals:
        user = db.query(User).get(inst.initiated_by)
        events.append({
            "timestamp": inst.created_at.isoformat() if inst.created_at else None,
            "type": "approval",
            "user": user.display_name if user else "未知",
            "user_id": inst.initiated_by,
            "action": "发起审批",
            "detail": f"审批流程状态: {inst.status}",
        })
        for step in inst.steps:
            if step.approved_at:
                approver = db.query(User).get(step.approver_id) if step.approver_id else None
                events.append({
                    "timestamp": step.approved_at.isoformat(),
                    "type": "approval",
                    "user": approver.display_name if approver else "未知",
                    "user_id": step.approver_id,
                    "action": f"审批{step.status}",
                    "detail": step.comment or "",
                })

    # 6. 异常记录
    exceptions = db.query(MESException).filter(MESException.wo_id == wo_id).all()
    for exc in exceptions:
        user = db.query(User).get(exc.reporter_id)
        events.append({
            "timestamp": exc.created_at.isoformat() if exc.created_at else None,
            "type": "exception",
            "user": user.display_name if user else "未知",
            "user_id": exc.reporter_id,
            "action": f"异常上报 ({exc.severity})",
            "detail": f"{exc.exception_type}: {exc.description[:200]}",
        })

    # 7. 审计日志（状态相关）
    audit_logs = db.query(AuditLog).filter(
        AuditLog.resource_type == "work_order",
        AuditLog.resource_id == wo_id,
    ).all()
    for log in audit_logs:
        events.append({
            "timestamp": log.created_at.isoformat() if hasattr(log, 'created_at') and log.created_at else None,
            "type": "audit",
            "user": log.operator or "系统",
            "action": log.action,
            "detail": log.detail or "",
        })

    # Sort by timestamp desc
    events.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    # Add icon and color
    for e in events:
        icon, color = TIMELINE_ICONS.get(e["type"], ("el-icon-info", "#999"))
        e["icon"] = icon
        e["color"] = color

    return events
