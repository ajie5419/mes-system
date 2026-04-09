import os
import uuid
import aiofiles
from pathlib import Path
from config import settings

ALLOWED_EXTENSIONS = {"pdf", "dwg", "dxf", "jpg", "png", "doc", "docx", "xls", "xlsx", "zip", "rar"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE
UPLOAD_DIR = settings.UPLOAD_DIR


def _ensure_dir(directory: str):
    path = Path(UPLOAD_DIR) / directory if directory else Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_file(filename: str, size: int) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: .{ext}，允许: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    if size > MAX_FILE_SIZE:
        raise ValueError(f"文件大小 {size} 超过限制 {MAX_FILE_SIZE} 字节")
    return ext


async def upload_file(file, directory: str = "") -> dict:
    ext = validate_file(file.filename or "", file.size or 0)
    target_dir = _ensure_dir(directory)
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    stored_path = target_dir / stored_name

    content = await file.read()
    async with aiofiles.open(stored_path, "wb") as f:
        await f.write(content)

    rel_path = f"{directory}/{stored_name}" if directory else stored_name
    return {
        "original_name": file.filename,
        "stored_path": rel_path,
        "file_size": len(content),
        "file_type": ext,
    }


def delete_file(file_path: str):
    full_path = Path(UPLOAD_DIR) / file_path
    if full_path.exists():
        os.remove(full_path)


def get_file_full_path(file_path: str):
    full_path = Path(UPLOAD_DIR) / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    return full_path
