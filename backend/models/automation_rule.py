from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from datetime import datetime
from database import Base


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(String(50), nullable=False, index=True,
                          comment="status_change/exception_created/due_date_approaching/progress_stalled")
    trigger_condition = Column(JSON, nullable=False, default=dict)
    action_type = Column(String(50), nullable=False,
                          comment="send_notification/create_task/escalate/change_status/assign_department")
    action_params = Column(JSON, nullable=False, default=dict)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AutomationExecutionLog(Base):
    __tablename__ = "automation_execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id"), nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=True)
    action_type = Column(String(50), nullable=False)
    action_params = Column(JSON, nullable=True)
    execution_status = Column(String(20), default="success", comment="success/failed/skipped")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
