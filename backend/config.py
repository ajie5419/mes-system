from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "制造业生产管理系统"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./mes.db"
    
    # 安全配置
    SECRET_KEY: str = "ALMA_SECRET_KEY_2026" # 实际环境应从环境变量读取
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
