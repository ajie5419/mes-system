from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class MilestoneTemplate(Base):
    __tablename__ = "milestone_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("work_order_templates.id"), nullable=False, index=True)
    node_name = Column(String(100), nullable=False)
    node_type = Column(String(50), default="执行")  # 审批/执行/检验/交付
    default_duration_days = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)

    template = relationship("WorkOrderTemplate", back_populates="milestones")


class WorkOrderTemplate(Base):
    __tablename__ = "work_order_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    industry_type = Column(String(100), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    milestones = relationship("MilestoneTemplate", back_populates="template", cascade="all, delete-orphan", order_by="MilestoneTemplate.sort_order")
