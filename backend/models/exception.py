from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Exception(Base):
    __tablename__ = "exceptions"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True, index=True)
    exception_type = Column(String(50), nullable=False, index=True, comment="物料短缺/设备故障/人员不足/质量异常/交期异常/其他")
    severity = Column(String(20), default="medium", index=True, comment="low/medium/high/critical")
    description = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="open", index=True, comment="open/in_progress/resolved/closed")
    root_cause = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    work_order = relationship("WorkOrder", backref="exceptions")
    department = relationship("Department")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
