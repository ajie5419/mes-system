from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from services import config_service

router = APIRouter(prefix="/system-config", tags=["system-config"])


class ConfigUpdate(BaseModel):
    key: str
    value: str
    group: str = "general"
    description: Optional[str] = None


@router.get("/")
def list_configs(group: Optional[str] = None, db: Session = Depends(get_db)):
    if group:
        return config_service.get_configs_by_group(db, group)
    # 返回所有配置按分组
    groups = ["system", "security", "notification", "work_order", "upload"]
    result = {}
    for g in groups:
        result[g] = config_service.get_configs_by_group(db, g)
    return result


@router.get("/value/{key}")
def get_config_value(key: str, db: Session = Depends(get_db)):
    val = config_service.get_config(db, key)
    if val is None:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"key": key, "value": val}


@router.put("/")
def update_config(data: ConfigUpdate, db: Session = Depends(get_db)):
    config_service.set_config(db, data.key, data.value, data.group, data.description or "")
    return {"message": "更新成功"}


@router.put("/batch")
def batch_update_configs(configs: List[ConfigUpdate], db: Session = Depends(get_db)):
    for c in configs:
        config_service.set_config(db, c.key, c.value, c.group, c.description or "")
    return {"message": f"成功更新 {len(configs)} 项配置"}
