from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models.system_config import SystemConfig


def get_config(db: Session, key: str, default: Any = None) -> Any:
    """获取配置值，支持默认值"""
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if cfg is None:
        return default
    return cfg.config_value


def set_config(db: Session, key: str, value: str, group: str = "general", description: str = ""):
    """设置配置（存在则更新，不存在则创建）"""
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if cfg:
        cfg.config_value = value
        if description:
            cfg.description = description
    else:
        cfg = SystemConfig(config_key=key, config_value=value, config_group=group, description=description)
        db.add(cfg)
    db.commit()


def get_configs_by_group(db: Session, group: str) -> List[Dict[str, Any]]:
    """按组获取配置"""
    configs = db.query(SystemConfig).filter(SystemConfig.config_group == group).order_by(SystemConfig.config_key).all()
    return [{"id": c.id, "key": c.config_key, "value": c.config_value, "description": c.description} for c in configs]


def init_default_configs(db: Session):
    """初始化默认系统配置"""
    defaults = [
        # JWT
        ("jwt_access_expire_minutes", "60", "security", "JWT访问令牌过期时间(分钟)"),
        ("jwt_refresh_expire_days", "7", "security", "JWT刷新令牌过期时间(天)"),
        # 通知
        ("notify_departments", '["生产部","采购部","项目管理部"]', "notification", "变更通知默认部门(JSON数组)"),
        # 工单
        ("default_template_id", "1", "work_order", "默认工单模板ID"),
        ("auto_generate_wo_number", "true", "work_order", "是否自动生成工单号"),
        # 文件上传
        ("max_file_size_mb", "50", "upload", "最大上传文件大小(MB)"),
        ("allowed_file_types", '["pdf","doc","docx","xls","xlsx","jpg","png","dwg","zip"]', "upload", "允许上传的文件类型(JSON数组)"),
        # 系统
        ("system_name", "制造业生产管理系统", "system", "系统名称"),
        ("version", "1.6.0", "system", "系统版本"),
    ]
    for key, value, group, desc in defaults:
        set_config(db, key, value, group, desc)
