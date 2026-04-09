from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ChangeRecord(Base):
    __tablename__ = "change_records"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    change_type = Column(String(30), nullable=False)    # 技术变更/工艺变更/计划变更
    description = Column(Text, nullable=False)
    initiated_by = Column(Integer, nullable=True)       # 发起人 user_id
    status = Column(String(30), default="Pending")      # Pending/Confirmed/Rejected
    created_at = Column(DateTime, default=datetime.now)

    confirmations = relationship("ChangeConfirmation", back_populates="change_record", cascade="all, delete-orphan")


class ChangeConfirmation(Base):
    __tablename__ = "change_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(Integer, ForeignKey("change_records.id"), nullable=False)
    department = Column(String(50), nullable=False)     # 需要确认的部门
    confirmed = Column(Boolean, default=False)
    confirmed_by = Column(Integer, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    change_record = relationship("ChangeRecord", back_populates="confirmations")
