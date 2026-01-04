from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, crawling, translating, generating, completed, failed
    articles_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(Text, nullable=True)


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    title_cn = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    content_cn = Column(Text, nullable=True)
    source_url = Column(String, nullable=False)
    publish_time = Column(DateTime(timezone=True), nullable=True)
    author = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)  # 译文音频路径
    audio_path_original = Column(String, nullable=True)  # 原文音频路径
    status = Column(String, default="pending")  # pending, translating, generating, completed, failed
    translation_progress = Column(Integer, default=0)  # 翻译进度 0-100
    translation_started_at = Column(DateTime(timezone=True), nullable=True)
    translation_completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Site(Base):
    __tablename__ = "sites"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    is_favorite = Column(Integer, default=0)  # 0 or 1
    created_at = Column(DateTime(timezone=True), server_default=func.now())

