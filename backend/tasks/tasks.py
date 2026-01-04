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
from spiders.reuters_spider import ReutersSpider
from spiders.generic_spider import GenericSpider
from config import settings
from datetime import datetime


def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # 在任务完成后关闭


@celery_app.task(bind=True)
def crawl_articles_task(self, task_id: str, url: str):
    """爬取文章任务"""
    db = get_db_session()
    try:
        # 更新任务状态
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return {"status": "error", "message": "Task not found"}
        
        task.status = "crawling"
        db.commit()
        
        # 根据URL选择爬虫
        spider = None
        if "reuters.com" in url:
            spider = ReutersSpider()
        else:
            spider = GenericSpider()
        
        # 爬取文章
        print(f"Starting to crawl articles from {url}")
        articles_data = spider.crawl(url, max_articles=settings.max_articles_per_task)
        print(f"Crawled {len(articles_data)} articles")
        
        # 如果爬取失败，更新任务状态并返回
        if not articles_data:
            print("No articles crawled from the website")
            task.status = "failed"
            task.error_message = "No articles found. The website may have anti-crawling protection or the URL is invalid."
            task.articles_count = 0
            db.commit()
            return {"status": "error", "message": "No articles found"}
        
        # 保存文章到数据库
        articles = []
        print(f"Saving {len(articles_data)} articles to database")
        for article_data in articles_data:
            article = models.Article(
                task_id=task_id,
                title=article_data.get("title", ""),
                content=article_data.get("content", ""),
                source_url=article_data.get("url", ""),
                publish_time=article_data.get("publish_time"),
                author=article_data.get("author"),
                status="pending"
            )
            db.add(article)
            articles.append(article)
        
        db.commit()
        
        # 更新任务状态
        task.articles_count = len(articles)
        task.status = "translating"
        db.commit()
        
        # 翻译文章
        for article in articles:
            try:
                article.status = "translating"
                db.commit()
                
                title_cn, content_cn = translation_service.translate_article(
                    article.title, article.content
                )
                article.title_cn = title_cn
                article.content_cn = content_cn
                article.status = "generating"
                db.commit()
                
                # 生成音频
                if article.content_cn:
                    audio_path = tts_service.text_to_speech(
                        article.content_cn, article.id, lang="zh"
                    )
                    article.audio_path = audio_path
                    article.status = "completed"
                    db.commit()
            except Exception as e:
                print(f"Error processing article {article.id}: {e}")
                article.status = "failed"
                db.commit()
        
        # 更新任务状态为完成
        task.status = "completed"
        db.commit()
        
        return {"status": "completed", "articles_count": len(articles)}
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Task error: {error_msg}")
        # 更新任务状态为失败
        try:
            task = db.query(models.Task).filter(models.Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = str(e)[:500]  # 限制错误消息长度
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
            status="translating"
        )
        db.add(article)
        db.commit()
        
        # 翻译文章
        try:
            title_cn, content_cn = translation_service.translate_article(title, content)
            article.title_cn = title_cn
            article.content_cn = content_cn
            article.status = "generating"
            db.commit()
            
            # 生成音频
            if article.content_cn:
                audio_path = tts_service.text_to_speech(
                    article.content_cn, article.id, lang="zh"
                )
                article.audio_path = audio_path
                article.status = "completed"
                db.commit()
        except Exception as e:
            print(f"Error processing article {article.id}: {e}")
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

