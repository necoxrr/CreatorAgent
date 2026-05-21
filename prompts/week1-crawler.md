@rules.md @skills/fastapi-craft.md @skills/vue-ui.md

本周任务：搭建CreatorAgent项目骨架 + 集成Firecrawl热点抓取。

请依次完成：
1. 初始化项目：Vue 3 + Vite + FastAPI + Supabase连接
   - 前端端口5173，后端8000
   - Supabase建表：hot_topics(id,title,url,platform,heat_score,crawled_at)
     和 creator_profiles(id,platform,style_vector,preferences)
2. 后端写Firecrawl集成模块 `apps/server/crawler/firecrawl_client.py`
   - API Key从环境变量读取
3. 写定时任务 `apps/server/crawler/scheduler.py`
   - 每天8:00、12:00、18:00自动抓取热搜
4. 前端热点列表页 `apps/web/src/views/TrendsView.vue`
   - 卡片展示，按热度排序，骨架屏+空态
5. 前后端联调：`GET /api/v1/trends`

先给出计划再动手，一步一步来。


---

## ⚠️ 实战踩坑（Claude Code 执行后自动追加）

> 格式：| 日期 | 问题（≤20字） | 解决（≤30字） | #标签 |

| 2026-05-21 | npm不认workspace协议导致install失败 | 重写package.json，去掉workspace:*引用 | #依赖问题 |
| 2026-05-21 | 目录多嵌套一层（apps/server/apps/） | rules.md明确指定apps/server/即后端根目录 | #目录结构 |
| 2026-05-21 | 前端框架需用Vue而非React | Vite+Vue3全栈重构，更新全部skill和prompt | #技术选型 |
| 2026-05-21 | Next.js页面Chrome报Unsafe attempt错误 | 补postcss.config.js和tsconfig.json后重启 | #环境配置 |
