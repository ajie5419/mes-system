from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from middleware.rbac import require_permission
from services import automation_service
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1/automation", tags=["自动化规则"])


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_condition: Dict[str, Any] = {}
    action_type: str
    action_params: Dict[str, Any] = {}
    is_enabled: Optional[bool] = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_condition: Optional[Dict[str, Any]] = None
    action_type: Optional[str] = None
    action_params: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    rules = automation_service.get_rules(db)
    return [{"id": r.id, "name": r.name, "description": r.description,
             "trigger_type": r.trigger_type, "trigger_condition": r.trigger_condition,
             "action_type": r.action_type, "action_params": r.action_params,
             "is_enabled": r.is_enabled, "created_at": str(r.created_at)}
            for r in rules]


@router.post("/rules")
def create_rule(data: RuleCreate, db: Session = Depends(get_db)):
    rule = automation_service.create_rule(db, data.model_dump())
    return {"id": rule.id, "message": "规则创建成功"}


@router.put("/rules/{rule_id}")
def update_rule(rule_id: int, data: RuleUpdate, db: Session = Depends(get_db)):
    rule = automation_service.update_rule(db, rule_id, data.model_dump(exclude_unset=True))
    if not rule:
        raise HTTPException(404, "规则不存在")
    return {"message": "规则更新成功"}


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    if not automation_service.delete_rule(db, rule_id):
        raise HTTPException(404, "规则不存在")
    return {"message": "规则已删除"}


@router.put("/rules/{rule_id}/toggle")
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = automation_service.toggle_rule(db, rule_id)
    if not rule:
        raise HTTPException(404, "规则不存在")
    return {"id": rule.id, "is_enabled": rule.is_enabled}


@router.get("/execution-log")
def execution_log(rule_id: Optional[int] = None, limit: int = Query(50, le=200),
                  db: Session = Depends(get_db)):
    logs = automation_service.get_execution_logs(db, rule_id=rule_id, limit=limit)
    return [{"id": l.id, "rule_id": l.rule_id, "rule_name": l.rule_name,
             "event_type": l.event_type, "event_data": l.event_data,
             "action_type": l.action_type, "execution_status": l.execution_status,
             "error_message": l.error_message, "created_at": str(l.created_at)}
            for l in logs]
