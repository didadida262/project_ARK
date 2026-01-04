from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./news_platform.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Settings
    translation_target_language: str = "zh"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

