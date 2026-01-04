# 新闻转换平台

一个自动化新闻采集、翻译和音频转换平台，帮助用户快速获取并消费国际主流媒体的最新新闻内容。

## 功能特性

- 🔍 自动爬取新闻网站最新文章（最多10篇）
- 🌐 自动翻译外文新闻为中文
- 🔊 将文章转换为音频文件
- 📥 支持下载原文、译文和音频
- 📱 响应式设计，支持移动端

## 技术栈

### 前端
- React 19
- Tailwind CSS
- Framer Motion
- React Router
- Axios

### 后端
- Python 3.9+
- FastAPI
- SQLAlchemy
- Celery + Redis
- Scrapy
- Google Translate (googletrans)
- gTTS (Google Text-to-Speech)

## 项目结构

```
project_ARK/
├── backend/              # 后端代码
│   ├── app/             # FastAPI应用
│   ├── services/        # 业务服务（翻译、TTS）
│   ├── tasks/           # Celery任务
│   ├── spiders/         # 爬虫模块
│   └── requirements.txt
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   └── api/         # API客户端
│   └── package.json
└── PRD.md               # 产品需求文档
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- Redis

**安装 Redis（macOS）：**
```bash
brew install redis
brew services start redis
```

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 创建环境变量文件（可选）：
```bash
cp .env.example .env
# 编辑 .env 文件，配置API密钥等
```

5. 初始化数据库：
```bash
python3 -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

6. 启动Redis（如果未运行）：
```bash
redis-server
```

7. 启动Celery Worker：
```bash
celery -A tasks.celery_app worker --loglevel=info
```

8. 启动FastAPI服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 创建环境变量文件（可选）：
```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

4. 启动开发服务器：
```bash
npm run dev
```

## 使用说明

1. 打开浏览器访问前端地址（默认 http://localhost:5173）
2. 输入新闻网站URL（如：https://www.reuters.com）
3. 点击"开始"按钮创建任务
4. 等待系统自动爬取、翻译和生成音频
5. 查看文章列表，点击文章查看详情
6. 下载原文、译文或音频文件

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 支持的网站

- 路透社 (Reuters) - 专用爬虫
- 其他新闻网站 - 通用爬虫（自动识别）

## 注意事项

1. **翻译服务**：使用免费的Google Translate API，可能有使用限制
2. **TTS服务**：使用gTTS，需要网络连接
3. **爬虫限制**：遵守robots.txt协议，控制爬取频率
4. **音频存储**：音频文件存储在 `backend/storage/audio/` 目录

## 开发计划

- [x] 基础架构搭建
- [x] 核心功能开发
- [x] 前端开发
- [ ] 测试与优化
- [ ] 部署上线

## 许可证

MIT License
