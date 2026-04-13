from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from config import settings
from database import engine, Base, SessionLocal
from routers import work_orders, changes, progress, dashboard, users, extra, auth, permissions, audit, upload, notifications, webhook, export, print, ws, bigscreen, departments, system_config, templates, task_board, approvals, exceptions, automation, comments, timeline, analytics
from middleware.rbac import require_permission
from services import permission_service, department_service, role_service, config_service, template_service, automation_service
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
        department_service.init_default_departments(db)
        role_service.init_default_roles(db)
        config_service.init_default_configs(db)
        template_service.init_default_template(db)
        automation_service.init_default_automation_rules(db)
    finally:
        db.close()
    logger.info("System initialized: RBAC, departments, roles, configs, templates")
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="1.5.0", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "系统繁忙", "detail": str(exc)})

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# 认证路由（无需认证）
app.include_router(auth.router, prefix="")
# 权限管理路由
app.include_router(permissions.router, prefix="")
# 业务路由（需认证+权限）
app.include_router(work_orders.router, prefix="")
app.include_router(changes.router, prefix="")
app.include_router(progress.router, prefix="")
app.include_router(dashboard.router, prefix="")
app.include_router(users.router, prefix="")
app.include_router(extra.router, prefix="")
app.include_router(audit.router, prefix="")
app.include_router(upload.router, prefix="")
app.include_router(notifications.router, prefix="")
app.include_router(webhook.router, prefix="")
app.include_router(export.router, prefix="")
app.include_router(print.router, prefix="")
app.include_router(bigscreen.router, prefix="")
# 系统管理路由
app.include_router(departments.router, prefix="")
app.include_router(system_config.router, prefix="")
app.include_router(templates.router, prefix="")
# WebSocket 路由
app.include_router(task_board.router, prefix="")
app.include_router(approvals.router, prefix="")
app.include_router(exceptions.router, prefix="")
app.include_router(ws.router, prefix="")
app.include_router(automation.router, prefix="")
app.include_router(comments.router, prefix="")
app.include_router(timeline.router, prefix="")
app.include_router(analytics.router, prefix="")

from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="frontend-assets")
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        from fastapi.responses import FileResponse
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/api-health")
def health_check():
    return {"status": "healthy", "version": "1.5.0"}
