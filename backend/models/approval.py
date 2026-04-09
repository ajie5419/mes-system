from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ApprovalFlow(Base):
    __tablename__ = "approval_flows"

    id = Column(Integer, primary_key=True, index=True)
    flow_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    steps_json = Column(JSON, nullable=False, comment="审批步骤定义 [{department_id, role?, approver_id?}]")
    created_at = Column(DateTime, default=datetime.now)

    instances = relationship("ApprovalInstance", back_populates="flow", cascade="all, delete-orphan")


class ApprovalInstance(Base):
    __tablename__ = "approval_instances"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("approval_flows.id"), nullable=False, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    current_step = Column(Integer, default=0, comment="当前步骤序号")
    status = Column(String(20), default="pending", index=True, comment="pending/approved/rejected")
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    flow = relationship("ApprovalFlow", back_populates="instances")
    steps = relationship("ApprovalStep", back_populates="instance", cascade="all, delete-orphan", order_by="ApprovalStep.step_order")


class ApprovalStep(Base):
    __tablename__ = "approval_steps"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("approval_instances.id"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="pending", comment="pending/approved/rejected")
    comment = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    instance = relationship("ApprovalInstance", back_populates="steps")
    department = relationship("Department")
    approver = relationship("User")
