from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── 供应商 ──
class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None
    rating: Optional[str] = "C"

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    rating: Optional[str] = None

class SupplierResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    rating: Optional[str]
    class Config: from_attributes = True

# ── 图纸 ──
class DrawingCreate(BaseModel):
    wo_id: int
    version: str = "V1.0"
    file_url: str = ""

class DrawingResponse(BaseModel):
    id: int
    wo_id: int
    version: str
    file_url: str
    created_at: datetime
    class Config: from_attributes = True

# ── 不合格品 ──
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
