from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import template_service

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    """获取所有工单模板"""
    templates = template_service.get_all_templates(db)
    result = []
    for t in templates:
        nodes = template_service.get_template_nodes(db, t.id)
        result.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "industry_type": t.industry_type,
            "is_default": t.is_default,
            "node_count": len(nodes),
        })
    return result


@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取模板详情（含里程碑节点）"""
    t = template_service.get_template(db, template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    nodes = [{"id": n.id, "node_name": n.node_name, "node_type": n.node_type,
              "default_duration_days": n.default_duration_days, "sort_order": n.sort_order,
              "is_required": n.is_required} for n in t.milestones]
    return {"id": t.id, "name": t.name, "description": t.description,
            "industry_type": t.industry_type, "is_default": t.is_default, "milestones": nodes}
