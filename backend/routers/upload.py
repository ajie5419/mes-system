import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models.file import UploadedFile
from models.user import User
from services.auth_service import get_current_user
from services import file_service
from middleware.rbac import require_permission
from middleware.audit import record
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/upload", tags=["文件上传"])


class DeleteFileRequest(BaseModel):
    file_path: str


@router.post("", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    directory: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("upload")),
    request: Request = None,
):
    try:
        info = await file_service.upload_file(file, directory)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = UploadedFile(
        original_name=info["original_name"],
        stored_path=info["stored_path"],
        file_size=info["file_size"],
        file_type=info["file_type"],
        uploaded_by=current_user.id,
        directory=directory,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "file_name": record.original_name,
        "file_path": record.stored_path,
        "file_size": record.file_size,
        "file_type": record.file_type,
        "uploaded_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("/{file_path:path}")
def download_file(
    file_path: str,
    current_user=Depends(require_permission("upload")),
):
    try:
        full_path = file_service.get_file_full_path(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(str(full_path), filename=os.path.basename(file_path))


@router.delete("", status_code=204)
def delete_file(
    body: DeleteFileRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission("upload")),
    request: Request = None,
):
    f = db.query(UploadedFile).filter(UploadedFile.stored_path == body.file_path).first()
    file_service.delete_file(body.file_path)
    if f:
        db.delete(f)
        db.commit()
    return None
