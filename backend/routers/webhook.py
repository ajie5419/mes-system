from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db
from services import auth_service
from services.webhook_service import get_webhook_configs, create_webhook_config, update_webhook_config, delete_webhook_config, send_wechat_webhook, send_dingtalk_webhook, send_webhook

router = APIRouter(prefix="/api/v1/webhook", tags=["Webhook"])


class WebhookCreate(BaseModel):
    name: str
    url: str
    type: str  # wechat/dingtalk/custom
    is_enabled: bool = True


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    is_enabled: Optional[bool] = None


class WebhookTest(BaseModel):
    config_id: int
    title: str = "测试消息"
    content: str = "这是一条 Webhook 测试消息"


def require_admin(current_user=Depends(auth_service.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(403, "仅管理员可操作")
    return current_user


@router.get("/config")
def list_configs(db: Session = Depends(get_db), _=Depends(require_admin)):
    configs = get_webhook_configs(db)
    return [{"id": c.id, "name": c.name, "url": c.url, "type": c.type, "is_enabled": c.is_enabled, "created_at": c.created_at.isoformat() if c.created_at else None} for c in configs]


@router.post("/config")
def add_config(data: WebhookCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = create_webhook_config(db, data.name, data.url, data.type, data.is_enabled)
    return {"id": c.id, "message": "创建成功"}


@router.put("/config/{config_id}")
def edit_config(config_id: int, data: WebhookUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = update_webhook_config(db, config_id, **data.model_dump(exclude_unset=True))
    if not c:
        raise HTTPException(404, "配置不存在")
    return {"message": "更新成功"}


@router.delete("/config/{config_id}")
def remove_config(config_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    if not delete_webhook_config(db, config_id):
        raise HTTPException(404, "配置不存在")
    return {"message": "删除成功"}


@router.post("/test")
def test_webhook(data: WebhookTest, db: Session = Depends(get_db), _=Depends(require_admin)):
    configs = get_webhook_configs(db)
    cfg = next((c for c in configs if c.id == data.config_id), None)
    if not cfg:
        raise HTTPException(404, "配置不存在")

    if cfg.type == "wechat":
        ok = send_wechat_webhook(cfg.url, data.title, data.content)
    elif cfg.type == "dingtalk":
        ok = send_dingtalk_webhook(cfg.url, data.title, data.content)
    else:
        ok = send_webhook(cfg.url, data.title, data.content, "info")
    return {"success": ok, "message": "发送成功" if ok else "发送失败"}
