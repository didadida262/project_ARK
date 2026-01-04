from celery import Celery
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

celery_app = Celery(
    "news_platform",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # 自动发现任务
    imports=('tasks.tasks',),
)

# 确保任务模块被导入
from tasks import tasks  # noqa

