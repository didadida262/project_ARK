#!/bin/bash

# 启动脚本

echo "启动Redis（如果未运行）..."
redis-server --daemonize yes 2>/dev/null || echo "Redis可能已在运行"

echo "启动Celery Worker..."
celery -A tasks.celery_app worker --loglevel=info --detach

echo "启动FastAPI服务器..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

