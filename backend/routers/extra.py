from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import get_current_user
from models.extra import Supplier, Drawing, QualityIssue
from models.file import UploadedFile
from services import file_service
from schemas.extra import (
    SupplierResponse, SupplierCreate, SupplierUpdate,
    DrawingResponse, DrawingCreate,
    QualityIssueResponse, QualityIssueCreate,
)
from middleware.rbac import require_permission
from middleware.audit import record
from fastapi import Request

router = APIRouter(prefix="/api/v1/extra", tags=["扩展模块"])

# ── 供应商 CRUD ──────────────────────────────────────────────
@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db), current_user = Depends(require_permission("extra:read"))):
    return db.query(Supplier).order_by(Supplier.id).all()

@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
def create_supplier(data: SupplierCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("extra:create"))):
    s = Supplier(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    record(db, current_user, "create", "supplier", s.id, data.model_dump(), request)
    return s

@router.put("/suppliers/{sid}", response_model=SupplierResponse)
def update_supplier(sid: int, data: SupplierUpdate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("extra:create"))):
    s = db.query(Supplier).get(sid)
    if not s:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    record(db, current_user, "update", "supplier", sid, data.model_dump(exclude_unset=True), request)
    return s

@router.delete("/suppliers/{sid}", status_code=204)
def delete_supplier(sid: int, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("extra:create"))):
    s = db.query(Supplier).get(sid)
    if not s:
        raise HTTPException(status_code=404, detail="供应商不存在")
    db.delete(s)
    db.commit()
    record(db, current_user, "delete", "supplier", sid, request=request)
    return None

# ── 图纸 ─────────────────────────────────────────────────────
@router.get("/drawings", response_model=list[DrawingResponse])
def list_drawings(db: Session = Depends(get_db), current_user = Depends(require_permission("extra:read"))):
    return db.query(Drawing).order_by(Drawing.id.desc()).all()

@router.post("/drawings", response_model=DrawingResponse, status_code=201)
async def create_drawing(
    wo_id: int = Form(...),
    version: str = Form("V1.0"),
    file_url: str = Form(""),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("extra:create")),
):
    uploaded_file_id = None
    actual_file_url = file_url
    if file and file.filename:
        try:
            info = await file_service.upload_file(file, directory="drawings")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        uf = UploadedFile(
            original_name=info["original_name"],
            stored_path=info["stored_path"],
            file_size=info["file_size"],
            file_type=info["file_type"],
            uploaded_by=current_user.id,
            directory="drawings",
        )
        db.add(uf)
        db.commit()
        db.refresh(uf)
        uploaded_file_id = uf.id
        actual_file_url = f"/uploads/{info['stored_path']}"

    d = Drawing(wo_id=wo_id, version=version, file_url=actual_file_url, uploaded_file_id=uploaded_file_id)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

# ── 不合格品项 ───────────────────────────────────────────────
@router.get("/quality-issues", response_model=list[QualityIssueResponse])
def list_quality_issues(db: Session = Depends(get_db), current_user = Depends(require_permission("extra:read"))):
    return db.query(QualityIssue).order_by(QualityIssue.id.desc()).all()

@router.post("/quality-issues", response_model=QualityIssueResponse)
def create_quality_issue(data: QualityIssueCreate, request: Request, db: Session = Depends(get_db), current_user = Depends(require_permission("extra:create"))):
    issue = QualityIssue(**data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    record(db, current_user, "create", "quality_issue", issue.id, data.model_dump(), request)
    return issue
