from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # wechat/dingtalk/custom
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
