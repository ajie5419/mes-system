from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupplierResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    rating: Optional[str]
    class Config: from_attributes = True

class DrawingResponse(BaseModel):
    id: int
    wo_id: int
    version: str
    file_url: str
    created_at: datetime
    class Config: from_attributes = True

class QualityIssueCreate(BaseModel):
    wo_id: int
    issue_type: str
    description: str

class QualityIssueResponse(BaseModel):
    id: int
    wo_id: int
    issue_type: str
    description: str
    status: str
    created_at: datetime
    class Config: from_attributes = True
