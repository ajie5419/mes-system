import httpx
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.webhook_config import WebhookConfig

logger = logging.getLogger(__name__)


def get_webhook_configs(db: Session) -> List[WebhookConfig]:
    return db.query(WebhookConfig).all()


def update_webhook_config(db: Session, config_id: int, **kwargs) -> Optional[WebhookConfig]:
    cfg = db.query(WebhookConfig).filter(WebhookConfig.id == config_id).first()
    if not cfg:
        return None
    for k, v in kwargs.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    db.commit()
    db.refresh(cfg)
    return cfg


def create_webhook_config(db: Session, name: str, url: str, type: str, is_enabled: bool = True) -> WebhookConfig:
    cfg = WebhookConfig(name=name, url=url, type=type, is_enabled=is_enabled)
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def delete_webhook_config(db: Session, config_id: int) -> bool:
    cfg = db.query(WebhookConfig).filter(WebhookConfig.id == config_id).first()
    if not cfg:
        return False
    db.delete(cfg)
    db.commit()
    return True


def send_webhook(url: str, title: str, content: str, type: str = "info") -> bool:
    """通用 Webhook 发送"""
    try:
        resp = httpx.post(url, json={"title": title, "content": content, "type": type}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Webhook 发送失败: {e}")
        return False


def send_wechat_webhook(url: str, title: str, content: str, mentioned_list: List[str] = None) -> bool:
    """企业微信 Webhook"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"## {title}\n\n{content}"
        }
    }
    if mentioned_list:
        payload["msgtype"] = "text"
        payload["text"] = {"content": f"【{title}】\n{content}", "mentioned_list": mentioned_list}
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"企业微信 Webhook 发送失败: {e}")
        return False


def send_dingtalk_webhook(url: str, title: str, content: str) -> bool:
    """钉钉 Webhook"""
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": f"### {title}\n\n{content}"}
    }
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"钉钉 Webhook 发送失败: {e}")
        return False


def send_to_enabled_webhooks(db: Session, title: str, content: str, type: str = "info", mentioned_list: List[str] = None) -> None:
    """向所有启用的 webhook 推送消息"""
    configs = db.query(WebhookConfig).filter(WebhookConfig.is_enabled == True).all()
    for cfg in configs:
        if cfg.type == "wechat":
            send_wechat_webhook(cfg.url, title, content, mentioned_list)
        elif cfg.type == "dingtalk":
            send_dingtalk_webhook(cfg.url, title, content)
        else:
            send_webhook(cfg.url, title, content, type)
