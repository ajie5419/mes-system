from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class WorkOrderAssignee(Base):
    __tablename__ = "work_order_assignees"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    role_in_wo = Column(String(50), nullable=False, comment="在工单中的角色：技术负责人/生产负责人/采购负责人/质量负责人等")
    assigned_at = Column(DateTime, default=datetime.now)

    work_order = relationship("WorkOrder", backref="assignees")
    user = relationship("User")
    department = relationship("Department")
