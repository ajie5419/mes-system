from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from database import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(50))
    rating = Column(String(10)) # A/B/C/D

class Drawing(Base):
    __tablename__ = "drawings"
    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"))
    version = Column(String(20))
    file_url = Column(String(500))
    uploaded_file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    created_at = Column(DateTime, default=datetime.now)

class QualityIssue(Base):
    __tablename__ = "quality_issues"
    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"))
    issue_type = Column(String(50)) # 制造缺陷/零部件缺陷/设计缺陷
    description = Column(Text)
    status = Column(String(20), default="Open") # Open/Closed
    created_at = Column(DateTime, default=datetime.now)
