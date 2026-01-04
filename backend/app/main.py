from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import sys

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.database import get_db, engine, Base
from app import models, schemas
from tasks.celery_app import celery_app
from tasks.tasks import process_text_task, generate_audio_task, generate_audio_task

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="新闻转换平台 API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于音频文件）
audio_storage_path = os.path.abspath("./storage/audio")
os.makedirs(audio_storage_path, exist_ok=True)
if os.path.exists(audio_storage_path):
    app.mount("/storage", StaticFiles(directory=audio_storage_path), name="storage")

@app.get("/")
async def root():
    return {"message": "新闻转换平台 API"}


@app.post("/api/tasks", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """创建新任务（仅文本模式）"""
    if not task.content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # 创建任务
    db_task = models.Task(url="text_input", status="pending")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 异步执行文本处理任务
    process_text_task.delay(db_task.id, task.title or "Untitled", task.content)
    
    # 转换字段名从id到task_id
    return schemas.TaskResponse.from_orm(db_task)


@app.get("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """获取任务状态"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return schemas.TaskResponse.from_orm(task)


@app.get("/api/tasks", response_model=schemas.TaskListResponse)
async def get_tasks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取任务列表"""
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    total = db.query(models.Task).count()
    return {
        "tasks": [schemas.TaskResponse.from_orm(t) for t in tasks],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@app.get("/api/tasks/{task_id}/articles", response_model=schemas.ArticleListResponse)
async def get_task_articles(task_id: str, db: Session = Depends(get_db)):
    """获取任务下的文章列表"""
    articles = db.query(models.Article).filter(models.Article.task_id == task_id).all()
    # 转换为响应模型
    article_responses = [schemas.ArticleResponse.from_orm(article) for article in articles]
    return {"articles": article_responses}


@app.delete("/api/tasks/all")
async def delete_all_tasks(db: Session = Depends(get_db)):
    """清空所有任务和文章"""
    try:
        # 先删除所有文章（因为有外键约束）
        articles_count = db.query(models.Article).count()
        db.query(models.Article).delete()
        
        # 再删除所有任务
        tasks_count = db.query(models.Task).count()
        db.query(models.Task).delete()
        
        db.commit()
        
        return {
            "message": "All tasks and articles deleted successfully",
            "deleted_tasks": tasks_count,
            "deleted_articles": articles_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting tasks: {str(e)}")


@app.get("/api/articles/{article_id}", response_model=schemas.ArticleDetailResponse)
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """获取文章详情"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/articles/{article_id}/download/original")
async def download_original(article_id: str, db: Session = Depends(get_db)):
    """下载原文"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 创建临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(f"{article.title}\n\n{article.content}")
        temp_path = f.name
    
    return FileResponse(
        temp_path,
        media_type='text/plain',
        filename=f"{article.title[:50]}_original.txt"
    )


@app.get("/api/articles/{article_id}/download/translated")
async def download_translated(article_id: str, db: Session = Depends(get_db)):
    """下载译文"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if not article.content_cn:
        raise HTTPException(status_code=400, detail="Translated content not available")
    
    # 创建临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(f"{article.title_cn or article.title}\n\n{article.content_cn}")
        temp_path = f.name
    
    return FileResponse(
        temp_path,
        media_type='text/plain',
        filename=f"{article.title_cn or article.title}_translated.txt"
    )


@app.post("/api/articles/{article_id}/generate-audio")
async def generate_audio(article_id: str, db: Session = Depends(get_db)):
    """生成文章音频"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if not article.content_cn:
        raise HTTPException(status_code=400, detail="Translated content not available")
    
    if article.audio_path and os.path.exists(article.audio_path):
        return {"message": "Audio already exists", "audio_path": article.audio_path}
    
    # 异步生成音频
    generate_audio_task.delay(article_id)
    
    return {"message": "Audio generation started"}


@app.get("/api/articles/{article_id}/download/audio")
async def download_audio(article_id: str, db: Session = Depends(get_db)):
    """下载音频"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if not article.audio_path or not os.path.exists(article.audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # 清理文件名中的特殊字符
    safe_filename = "".join(c for c in (article.title_cn or article.title or "article") if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename[:50]  # 限制长度
    if not safe_filename:
        safe_filename = "article"
    
    return FileResponse(
        article.audio_path,
        media_type='audio/mpeg',
        filename=f"{safe_filename}.mp3"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

