from celery import Task
from sqlalchemy.orm import Session
import sys
import os

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from tasks.celery_app import celery_app
from app.database import SessionLocal
from app import models
from services.translation_service import translation_service
from services.tts_service import tts_service
from config import settings
from datetime import datetime


def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # 在任务完成后关闭


@celery_app.task(bind=True)
def process_text_task(self, task_id: str, title: str, content: str):
    """处理文本输入任务"""
    db = get_db_session()
    try:
        # 更新任务状态
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return {"status": "error", "message": "Task not found"}
        
        task.status = "translating"
        task.articles_count = 1
        db.commit()
        
        # 创建文章记录
        article = models.Article(
            task_id=task_id,
            title=title,
            content=content,
            source_url="text_input",
            publish_time=datetime.now(),
            author=None,
            status="translating",
            translation_progress=0,
            translation_started_at=datetime.now()
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        
        # 定义进度回调函数
        def update_progress(progress: int):
            """更新翻译进度 (0-100)"""
            try:
                # 重新获取数据库会话（避免会话问题）
                article_update = db.query(models.Article).filter(models.Article.id == article.id).first()
                if article_update:
                    article_update.translation_progress = progress
                    db.commit()
                    print(f"Translation progress: {progress}%")
            except Exception as e:
                print(f"Error updating progress: {e}")
        
        # 翻译文章
        try:
            title_cn, content_cn = translation_service.translate_article(title, content, progress_callback=update_progress)
            article.title_cn = title_cn
            article.content_cn = content_cn
            article.translation_progress = 100
            article.translation_completed_at = datetime.now()
            # 翻译完成后直接标记为完成
            article.status = "completed"
            db.commit()
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"Error processing article {article.id}: {error_msg}")
            # 即使翻译异常，也尝试保存已翻译的内容（如果有的话）
            try:
                # 如果翻译过程中出现异常，但部分内容已翻译，使用原文作为fallback
                if not article.title_cn:
                    article.title_cn = title
                if not article.content_cn:
                    article.content_cn = content
                article.translation_completed_at = datetime.now()
                # 标记为完成而不是失败（因为至少保存了原文）
                article.status = "completed"
                article.translation_progress = 100
                db.commit()
            except:
                # 如果保存也失败，才标记为失败
                article.status = "failed"
                db.commit()
        
        # 更新任务状态为完成
        task.status = "completed"
        db.commit()
        
        return {"status": "completed", "articles_count": 1}
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Task error: {error_msg}")
        # 更新任务状态为失败
        try:
            task = db.query(models.Task).filter(models.Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = str(e)[:500]
                db.commit()
        except:
            pass
        return {"status": "error", "message": str(e)}
    finally:
        try:
            db.close()
        except:
            pass


@celery_app.task(bind=True)
def generate_audio_task(self, article_id: str, text_type: str = "translated"):
    """生成音频任务
    
    Args:
        article_id: 文章ID
        text_type: 文本类型，'original' 或 'translated'
    """
    db = get_db_session()
    try:
        article = db.query(models.Article).filter(models.Article.id == article_id).first()
        if not article:
            return {"status": "error", "message": "Article not found"}
        
        # 选择要生成音频的文本
        if text_type == "translated":
            if not article.content_cn:
                return {"status": "error", "message": "Translated content not available"}
            text_to_convert = article.content_cn
            lang = "zh"  # 中文
            audio_filename_suffix = ""
        else:  # original
            if not article.content:
                return {"status": "error", "message": "Original content not available"}
            text_to_convert = article.content
            lang = "en"  # 英文（可以根据实际情况调整）
            audio_filename_suffix = "_original"
        
        # 更新文章状态为生成中
        article.status = "generating"
        db.commit()
        
        # 定义进度回调函数
        def update_progress(progress: int):
            """更新音频生成进度 (0-100)"""
            try:
                article_update = db.query(models.Article).filter(models.Article.id == article_id).first()
                if article_update:
                    # 使用translation_progress字段存储音频生成进度（临时）
                    article_update.translation_progress = progress
                    db.commit()
                    print(f"Audio generation progress: {progress}%")
            except Exception as e:
                print(f"Error updating audio progress: {e}")
        
        # 生成音频
        try:
            print(f"Starting audio generation for article {article_id} ({text_type})...")
            print(f"Content length: {len(text_to_convert)} characters")
            
            audio_path = tts_service.text_to_speech(
                text_to_convert, 
                f"{article_id}{audio_filename_suffix}", 
                lang=lang,
                progress_callback=update_progress
            )
            
            print(f"✓ Audio generation completed: {audio_path}")
            
            # 保存音频路径
            if text_type == "translated":
                article.audio_path = audio_path
            else:  # original
                article.audio_path_original = audio_path
            
            article.status = "completed"
            article.translation_progress = 100
            db.commit()
            return {"status": "completed", "audio_path": audio_path, "text_type": text_type}
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"✗ Error generating audio for article {article_id}: {error_msg}")
            # 即使音频生成失败，也标记为完成（因为翻译已完成）
            article.status = "completed"
            article.translation_progress = 0  # 重置进度
            db.commit()
            return {"status": "error", "message": str(e)}
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Audio generation task error: {error_msg}")
        return {"status": "error", "message": str(e)}
    finally:
        try:
            db.close()
        except:
            pass
