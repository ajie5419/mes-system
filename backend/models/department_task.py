from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base


class DepartmentTask(Base):
    __tablename__ = "department_tasks"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", index=True, comment="pending/in_progress/completed/overdue")
    priority = Column(Integer, default=3, comment="1-5, 1最高")
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    work_order = relationship("WorkOrder", backref="department_tasks")
    department = relationship("Department")
    assignee = relationship("User")
