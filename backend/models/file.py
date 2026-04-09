from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(500), nullable=False)
    stored_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(20))
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    directory = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.now)
