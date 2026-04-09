from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routers import work_orders, changes, progress, dashboard, users, extra
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.3.0")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "系统繁忙", "detail": str(exc)})

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(work_orders.router)
app.include_router(changes.router)
app.include_router(progress.router)
app.include_router(dashboard.router)
app.include_router(users.router)
app.include_router(extra.router)

@app.get("/")
def health_check():
    return {"status": "healthy", "version": "1.3.0"}
