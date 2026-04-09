from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from models.approval import ApprovalFlow, ApprovalInstance, ApprovalStep


def create_approval_flow(db: Session, flow_name: str, description: str, steps: list) -> ApprovalFlow:
    flow = ApprovalFlow(flow_name=flow_name, description=description, steps_json=steps)
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return flow


def get_approval_flows(db: Session) -> List[ApprovalFlow]:
    return db.query(ApprovalFlow).order_by(ApprovalFlow.created_at.desc()).all()


def start_approval(db: Session, flow_id: int, wo_id: int, initiated_by: int) -> ApprovalInstance:
    flow = db.query(ApprovalFlow).filter(ApprovalFlow.id == flow_id).first()
    if not flow:
        raise ValueError("审批流不存在")
    instance = ApprovalInstance(flow_id=flow_id, wo_id=wo_id, current_step=0, status="pending", initiated_by=initiated_by)
    db.add(instance)
    db.flush()
    for idx, step_def in enumerate(flow.steps_json):
        s = ApprovalStep(
            instance_id=instance.id, step_order=idx,
            department_id=step_def.get("department_id"),
            approver_id=step_def.get("approver_id"),
        )
        db.add(s)
    db.commit()
    db.refresh(instance)
    return instance


def approve_step(db: Session, step_id: int, user_id: int, comment: str = None) -> Optional[ApprovalStep]:
    step = db.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
    if not step:
        return None
    if step.status != "pending":
        raise ValueError("该步骤已审批")
    if step.approver_id and step.approver_id != user_id:
        raise ValueError("无权审批此步骤")
    step.status = "approved"
    step.comment = comment
    step.approved_at = datetime.now()
    # check if all steps done
    instance = step.instance
    all_approved = all(s.status == "approved" for s in instance.steps)
    if all_approved:
        instance.status = "approved"
    else:
        # advance current_step
        pending = [s for s in instance.steps if s.status == "pending"]
        if pending:
            instance.current_step = pending[0].step_order
    db.commit()
    db.refresh(step)
    return step


def reject_step(db: Session, step_id: int, user_id: int, comment: str = None) -> Optional[ApprovalStep]:
    step = db.query(ApprovalStep).filter(ApprovalStep.id == step_id).first()
    if not step:
        return None
    if step.status != "pending":
        raise ValueError("该步骤已审批")
    if step.approver_id and step.approver_id != user_id:
        raise ValueError("无权审批此步骤")
    step.status = "rejected"
    step.comment = comment
    step.approved_at = datetime.now()
    step.instance.status = "rejected"
    db.commit()
    db.refresh(step)
    return step


def get_pending_approvals(db: Session, user_id: int) -> list:
    steps = db.query(ApprovalStep).filter(
        ApprovalStep.status == "pending",
        ApprovalStep.approver_id == user_id,
    ).order_by(ApprovalStep.step_order).all()
    result = []
    for s in steps:
        result.append({
            "step_id": s.id, "step_order": s.step_order,
            "instance_id": s.instance_id, "wo_id": s.instance.wo_id,
            "flow_name": s.instance.flow.flow_name,
            "department_id": s.department_id,
            "department_name": s.department.name if s.department else None,
            "created_at": s.instance.created_at,
        })
    return result


def get_approval_history(db: Session, wo_id: int) -> list:
    instances = db.query(ApprovalInstance).filter(ApprovalInstance.wo_id == wo_id).order_by(ApprovalInstance.created_at.desc()).all()
    result = []
    for inst in instances:
        steps_data = []
        for s in inst.steps:
            steps_data.append({
                "step_order": s.step_order,
                "department_name": s.department.name if s.department else None,
                "approver_name": s.approver.display_name if s.approver else None,
                "status": s.status,
                "comment": s.comment,
                "approved_at": s.approved_at,
            })
        result.append({
            "instance_id": inst.id,
            "flow_name": inst.flow.flow_name,
            "status": inst.status,
            "initiated_by": inst.initiated_by,
            "created_at": inst.created_at,
            "steps": steps_data,
        })
    return result
