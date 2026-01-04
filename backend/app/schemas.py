from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    url: str


class TaskResponse(BaseModel):
    task_id: str
    url: str
    status: str
    articles_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
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
    audio_path: Optional[str] = None
    status: str
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
    audio_path: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BatchDownloadRequest(BaseModel):
    article_ids: List[str]
    format: str = "zip"

