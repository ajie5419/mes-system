from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "制造业生产管理系统"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://mes:mes123@localhost:5432/mes_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # 安全配置
    SECRET_KEY: str = "ALMA_SECRET_KEY_2026"
    JWT_SECRET_KEY: str = "mes_jwt_dev_secret_key_change_in_production_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024

    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
