from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    node_name = Column(String(100), nullable=False)      # 技术出图/工艺编制/物料采购...
    sort_order = Column(Integer, default=0)
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    completion_rate = Column(Float, default=0.0)          # 0-100
    deviation_days = Column(Integer, default=0)           # 正数=延期, 负数=提前
    status = Column(String(20), default="Pending")        # Pending/InProgress/Completed

    work_order = relationship("WorkOrder", back_populates="milestones")
