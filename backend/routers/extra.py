from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.extra import Supplier, Drawing, QualityIssue
from ..schemas.extra import SupplierResponse, DrawingResponse, QualityIssueResponse, QualityIssueCreate

router = APIRouter(prefix="/api/v1/extra", tags=["扩展模块"])

@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

@router.get("/drawings", response_model=list[DrawingResponse])
def list_drawings(db: Session = Depends(get_db)):
    return db.query(Drawing).all()

@router.get("/quality-issues", response_model=list[QualityIssueResponse])
def list_quality_issues(db: Session = Depends(get_db)):
    return db.query(QualityIssue).all()

@router.post("/quality-issues", response_model=QualityIssueResponse)
def create_quality_issue(data: QualityIssueCreate, db: Session = Depends(get_db)):
    issue = QualityIssue(**data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue
