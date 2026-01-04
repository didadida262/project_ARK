from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    title: Optional[str] = None
    content: str


class TaskResponse(BaseModel):
    task_id: str
    url: str
    status: str
    articles_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应对象"""
        return cls(
            task_id=obj.id,
            url=obj.url,
            status=obj.status,
            articles_count=obj.articles_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            error_message=obj.error_message
        )
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int


class ArticleResponse(BaseModel):
    id: str
    task_id: str
    title: str
    title_cn: Optional[str] = None
    content: Optional[str] = None
    content_cn: Optional[str] = None
    source_url: str
    publish_time: Optional[datetime] = None
    author: Optional[str] = None
    audio_path: Optional[str] = None  # 译文音频路径
    audio_path_original: Optional[str] = None  # 原文音频路径
    status: str
    translation_progress: Optional[int] = 0
    translation_started_at: Optional[datetime] = None
    translation_completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]


class ArticleDetailResponse(BaseModel):
    id: str
    task_id: str
    title: str
    title_cn: Optional[str] = None
    content: str
    content_cn: Optional[str] = None
    source_url: str
    publish_time: Optional[datetime] = None
    author: Optional[str] = None
    audio_path: Optional[str] = None  # 译文音频路径
    audio_path_original: Optional[str] = None  # 原文音频路径
    status: str
    translation_progress: Optional[int] = 0
    translation_started_at: Optional[datetime] = None
    translation_completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BatchDownloadRequest(BaseModel):
    article_ids: List[str]
    format: str = "zip"

