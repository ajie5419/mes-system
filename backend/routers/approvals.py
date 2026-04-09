from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from services import approval_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


class FlowCreate(BaseModel):
    flow_name: str
    description: Optional[str] = None
    steps: List[dict]


class ApprovalAction(BaseModel):
    user_id: int
    comment: Optional[str] = None


class StartApproval(BaseModel):
    flow_id: int
    wo_id: int
    initiated_by: int


@router.get("/flows")
def list_flows(db: Session = Depends(get_db)):
    flows = approval_service.get_approval_flows(db)
    return [{"id": f.id, "flow_name": f.flow_name, "description": f.description, "steps": f.steps_json, "created_at": str(f.created_at)} for f in flows]


@router.post("/flows")
def create_flow(data: FlowCreate, db: Session = Depends(get_db)):
    flow = approval_service.create_approval_flow(db, data.flow_name, data.description or "", data.steps)
    return {"id": flow.id, "message": "创建成功"}


@router.post("/start")
def start_approval(data: StartApproval, db: Session = Depends(get_db)):
    try:
        inst = approval_service.start_approval(db, data.flow_id, data.wo_id, data.initiated_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"instance_id": inst.id, "message": "审批已发起"}


@router.get("/pending")
def pending_approvals(user_id: int, db: Session = Depends(get_db)):
    return approval_service.get_pending_approvals(db, user_id)


@router.get("/history/{wo_id}")
def approval_history(wo_id: int, db: Session = Depends(get_db)):
    return approval_service.get_approval_history(db, wo_id)


@router.post("/steps/{step_id}/approve")
def approve(step_id: int, data: ApprovalAction, db: Session = Depends(get_db)):
    try:
        step = approval_service.approve_step(db, step_id, data.user_id, data.comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not step:
        raise HTTPException(status_code=404, detail="步骤不存在")
    return {"message": "审批通过"}


@router.post("/steps/{step_id}/reject")
def reject(step_id: int, data: ApprovalAction, db: Session = Depends(get_db)):
    try:
        step = approval_service.reject_step(db, step_id, data.user_id, data.comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not step:
        raise HTTPException(status_code=404, detail="步骤不存在")
    return {"message": "已驳回"}
