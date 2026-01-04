from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./news_platform.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys
    google_translate_api_key: Optional[str] = None
    deepl_api_key: Optional[str] = None
    baidu_translate_app_id: Optional[str] = None
    baidu_translate_secret_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    
    # Settings
    max_articles_per_task: int = 10
    translation_target_language: str = "zh"
    audio_format: str = "mp3"
    
    # File Storage
    audio_storage_path: str = "./storage/audio"
    upload_storage_path: str = "./storage/uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

