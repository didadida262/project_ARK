# 快速启动指南

## 1. 安装依赖

### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 前端
```bash
cd frontend
npm install
```

## 2. 启动服务

### 启动Redis（必需）

如果未安装 Redis，使用 Homebrew 安装：
```bash
brew install redis
```

启动 Redis：
```bash
brew services start redis
# 或者直接运行（不设置为服务）：
# redis-server
```

验证 Redis 是否运行：
```bash
redis-cli ping
# 应该返回 PONG
```

### 启动Celery Worker（新终端窗口）
```bash
cd backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

### 启动后端API（新终端窗口）
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端（新终端窗口）
```bash
cd frontend
npm run dev
```

## 3. 访问应用

- 前端：http://localhost:5173
- 后端API文档：http://localhost:8000/docs

## 4. 使用示例

1. 打开浏览器访问前端地址
2. 输入新闻网站URL，例如：`https://www.reuters.com`
3. 点击"开始"按钮
4. 等待任务完成（爬取 → 翻译 → 生成音频）
5. 查看文章列表并下载内容

## 注意事项

- 确保Redis服务正在运行
- 首次运行会自动创建数据库
- 翻译和TTS需要网络连接
- 音频文件存储在 `backend/storage/audio/` 目录

