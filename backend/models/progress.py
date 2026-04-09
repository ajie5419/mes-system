from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from datetime import datetime
from database import Base


class ProgressReport(Base):
    __tablename__ = "progress_reports"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    reported_by = Column(Integer, nullable=True)         # 汇报人 user_id
    team_name = Column(String(100))                      # 班组名称
    completion_rate = Column(Float, nullable=False)      # 本次汇报的完成率
    remark = Column(String(500), nullable=True)
    report_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
