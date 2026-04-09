from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from ..constants import WorkOrderStatus, HealthStatus

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    wo_number = Column(String(50), unique=True, nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    customer_name = Column(String(100))
    priority = Column(Integer, default=3)
    status = Column(String(20), default=WorkOrderStatus.BACKLOG.value)
    current_stage = Column(String(50), default="待排产")
    is_locked = Column(Boolean, default=False)
    total_progress = Column(Float, default=0.0)
    health_status = Column(String(10), default=HealthStatus.GREEN.value)
    planned_delivery_date = Column(Date)
    actual_delivery_date = Column(Date, nullable=True)
    technical_manager_id = Column(Integer, nullable=True)
    production_manager_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    milestones = relationship("Milestone", back_populates="work_order", cascade="all, delete-orphan")
