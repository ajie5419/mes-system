from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config import settings
from database import engine, Base, SessionLocal
from routers import work_orders, changes, progress, dashboard, users, extra, auth, permissions, audit, upload, notifications, webhook, export, print, ws, bigscreen
from middleware.rbac import require_permission
from services import permission_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        permission_service.init_default_permissions(db)
        permission_service.init_role_permissions(db)
    finally:
        db.close()
    logger.info("RBAC permissions initialized")
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="1.5.0", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "系统繁忙", "detail": str(exc)})

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# 认证路由（无需认证）
app.include_router(auth.router)
# 权限管理路由
app.include_router(permissions.router)
# 业务路由（需认证+权限）
app.include_router(work_orders.router)
app.include_router(changes.router)
app.include_router(progress.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(extra.router)
app.include_router(audit.router)
app.include_router(upload.router)
app.include_router(notifications.router)
app.include_router(webhook.router)
app.include_router(export.router)
app.include_router(print.router)
app.include_router(bigscreen.router)
# WebSocket 路由
app.include_router(ws.router)

from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
def health_check():
    return {"status": "healthy", "version": "1.5.0"}
