# 快速启动指南

## 前置要求
- Python 3.9+
- Node.js 18+
- Redis

## 一键安装

```bash
# 1. 安装后端依赖
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 安装前端依赖
cd ../frontend
npm install

# 3. 安装并启动Redis（macOS）
brew install redis && brew services start redis
```

## 启动服务（需要3个终端窗口）

### 终端1：Celery Worker
```bash
cd backend && source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

### 终端2：后端API
```bash
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 终端3：前端
```bash
cd frontend && npm run dev
```

## 访问

- **前端应用**：http://localhost:5173
- **API文档**：http://localhost:8000/docs

## 使用

1. 访问前端页面
2. 输入新闻网站URL（如：`https://www.reuters.com`）
3. 点击"开始"，等待处理完成
4. 查看文章和下载内容

## 提示

- 确保Redis运行：`redis-cli ping`（应返回PONG）
- 首次运行自动创建数据库
- 需要网络连接（翻译和TTS服务）

