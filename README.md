# 文章翻译平台

一个简洁的文章翻译平台，支持用户输入文章内容，自动翻译成中文。

## 功能特性

- ✍️ 支持文本输入，直接输入文章内容
- 🌐 自动翻译外文文章为中文
- 📥 支持下载原文和译文
- 📱 响应式设计，支持移动端
- ⚡ 异步处理，支持长文本分段翻译

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
- Argos Translate (离线翻译)

## 项目结构

```
project_ARK/
├── backend/              # 后端代码
│   ├── app/             # FastAPI应用
│   ├── services/        # 业务服务（翻译）
│   ├── tasks/           # Celery任务
│   └── requirements.txt
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   └── api/         # API客户端
│   └── package.json
└── README.md            # 项目说明
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
2. 输入文章标题（可选）和文章内容
3. 点击"开始翻译"按钮创建任务
4. 等待系统自动翻译成中文
5. 查看文章详情
6. 下载原文或译文文件

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 注意事项

1. **翻译服务**：使用Argos Translate离线翻译，无需网络连接，保护隐私
2. **语言包安装**：首次使用时需要下载语言包（自动安装），后续使用无需网络
3. **长文本处理**：对于长文本（>1000字符），系统会自动分段翻译以提高速度
4. **异步处理**：使用Celery进行异步任务处理，支持并发翻译

## 开发计划

- [x] 基础架构搭建
- [x] 核心功能开发
- [x] 前端开发
- [ ] 测试与优化
- [ ] 部署上线

## 许可证

MIT License
