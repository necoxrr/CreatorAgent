# CreatorAgent

面向小红书/抖音创作者的 AI 智能体平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + TailwindCSS + Pinia + Vue Router |
| 后端 | FastAPI + Python 3.10+ |
| 数据库 | Supabase (PostgreSQL) |
| 检索 | ChromaDB (向量数据库) + sentence-transformers (本地 Embedding) |
| 爬虫 | Firecrawl |

## 项目结构

```
CreatorAgent/
├── apps/
│   ├── web/                 # Vue 3 前端
│   │   └── src/
│   │       ├── views/       # 页面视图
│   │       │   ├── HomeView.vue
│   │       │   ├── TrendsView.vue      # 热点趋势
│   │       │   ├── TopicsView.vue       # 选题推荐
│   │       │   ├── DashboardView.vue
│   │       │   └── EditorView.vue
│   │       ├── components/  # 组件
│   │       ├── composables/ # 组合式函数
│   │       ├── stores/      # Pinia 状态管理
│   │       ├── api/         # API 封装
│   │       └── router/      # 路由配置
│   └── server/              # FastAPI 后端
│       └── apps/
│           ├── main.py      # 应用入口
│           ├── config.py    # 配置管理
│           ├── api/v1/      # API 路由
│           │   ├── trends.py  # 热点趋势 API
│           │   └── topics.py  # 选题推荐 API
│           ├── crawler/     # 内容爬虫
│           ├── db/          # Supabase 数据库操作
│           ├── models/      # Pydantic 数据模型
│           └── rag/         # RAG 检索引擎
├── packages/
│   └── shared/              # 共享类型定义
├── prompts/                 # 提示词模板（按开发阶段）
└── supabase/                # Supabase 配置
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- pip

### 1. 克隆 & 安装依赖

```bash
# 前端
cd apps/web
npm install

# 后端
cd ../server
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cd apps/server
cp .env.example .env
```

编辑 `.env` 填写必要配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SUPABASE_URL` | Supabase 项目地址 | 必填 |
| `SUPABASE_KEY` | Supabase API Key | 必填 |
| `EMBEDDING_PROVIDER` | `local` 或 `openai` | `local` |
| `FIRECRAWL_API_KEY` | Firecrawl 爬虫 Key | 可选 |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务监听端口 | `8000` |

### 3. 启动服务

**后端：**
```bash
cd apps/server
uvicorn apps.main:app --host 0.0.0.0 --port 8000 --reload
```

**前端：**
```bash
cd apps/web
npm run dev
```

或使用 npm workspaces（需开两个终端）：

```bash
# 终端1
npm run dev:server

# 终端2
npm run dev:web
```

### 4. 访问

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 功能模块

### 1. 热点趋势 (Trends)
- 实时爬取小红书/抖音热门内容
- 按类目筛选（美妆、穿搭、美食、旅行等）
- 趋势数据可视化

### 2. 选题推荐 (Topics)
- 基于 ChromaDB 语义检索
- 支持本地 Embedding 模型（sentence-transformers）
- 支持 OpenAI Embedding（可选）
- 关联优质内容进行智能推荐

### 3. 内容编辑 (Editor)
- Markdown 富文本编辑
- 一键发布到小红书/抖音

## API 列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/trends` | 获取热点趋势 |
| POST | `/api/v1/topics/recommend` | 选题推荐 |
| GET | `/api/v1/topics/search` | 语义搜索 |

## 开发说明

### 使用 npm workspaces

项目根目录 `package.json` 配置了 workspaces：

```json
{
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev:web": "npm run dev --workspace=apps/web",
    "dev:server": "npm run dev --workspace=apps/server",
    "build": "npm run build --workspace=apps/web"
  }
}
```

### 添加新的 API 路由

1. 在 `apps/server/apps/api/v1/` 下创建新路由文件
2. 注册到 `apps/server/apps/main.py` 的 `app.include_router()`

### 前端请求后端

前端通过 `axios` 调用 `http://localhost:8000` 接口，CORS 已配置允许 `localhost:5173`。