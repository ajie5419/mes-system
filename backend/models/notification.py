from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime
from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    type = Column(String(20), nullable=False, default="info")  # info/warning/error/success
    is_read = Column(Boolean, default=False)
    related_resource_type = Column(String(50), nullable=True)  # work_order/change/progress等
    related_resource_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
