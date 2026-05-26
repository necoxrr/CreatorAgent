# 🎤 面试故事集

> 每个故事按 STAR 格式（Situation → Task → Action → Result）。
> 来源：docs/inspirations.md 中 #面试素材 标签的条目。
> 每周日自动整理，每个故事≤200字。

---

## 故事列表
（Claude Code 每周自动追加）

| 日期 | 标题 | 标签 |
|------|------|------|
| 2026-05-22 | 国产化Embedding方案：从OpenAI API到本地模型 | #面试素材 |
| 2026-05-22 | Supabase RLS 生产事故：一条SQL引发的血案 | #面试素材 |
| 2026-05-26 | LangGraph 异步节点死锁：从同步到异步的艰难迁移 | #面试素材 |

---

## 故事详情

### 2026-05-22 | 国产化Embedding方案：从OpenAI API到本地模型

**Situation（背景）**
CreatorAgent 选题推荐模块需要文本向量化能力，原本调用 OpenAI text-embedding-3-small API。但部署到国内服务器时，大量请求因网络超时（huggingface.co / api.openai.com）失败，用户体验断崖式下跌。

**Task（任务）**
设计一套可在无外网或低网络质量环境下工作的 Embedding 方案，保证推荐功能在国内可用，同时保持接口抽象层不变，便于未来切换。

**Action（行动）**
1. **抽象 provider 层**：在 `embedder.py` 设计 `BaseEmbedder` 基类 + `OpenAIEmbedder` / `LocalEmbedder` 双实现，通过 `EMBEDDING_PROVIDER` 环境变量切换，调用方无感知。
2. **选型本地模型**：选用 `sentence-transformers/all-MiniLM-L6-v2`（384维，~80MB），在首次加载后缓存到本地，后续推理完全离线。
3. **修复 ChromaDB 兼容性**：新版 ChromaDB 要求 metadata 非空，修复了 `add_documents` 的空字典判断；维度从 1536（OpenAI）切换到 384（local）后，重建 collection 并手动 reindex。
4. **加权排序**：在 topic_engine 的综合打分中，注入 ChromaDB 语义检索的 `distance` → `similarity` 因子，使关键词检索结果真正影响排序。

**Result（结果）**
- Embedding 请求从依赖外网变为完全本地化，延迟从数秒降到毫秒级
- 通过环境变量一行配置即可切换 provider，无需改业务代码
- 25 个单元测试覆盖 Embedder / VectorStore / TopicEngine 三个模块

**可面试讲的点**：
- "怎么设计一个可插拔的 provider 架构"——抽象基类 + 工厂模式 + lru_cache 单例
- "遇到网络不可用时的降级策略"——ChromaDB 为空时 fallback 到 Supabase 热榜排序
- "向量维度变更时的数据迁移"——force_recreate + 手动 reindex 脚本

### 2026-05-22 | Supabase RLS 生产事故：一条SQL引发的血案

**Situation（背景）**
数据已经通过 Supabase Dashboard 手动插入，代码层面一切正常，但 Python 脚本执行 insert 时始终报错：`new row violates row-level security policy for table "hot_topics"`。同时后端 API 响应「无数据」，前端页面空白。

**Task（任务）**
定位插入失败的根本原因，修复数据入库通道，确保后续爬虫抓取的数据能正常写入数据库。

**Action（行动）**
1. **分层排查**：先确认 Supabase 客户端初始化正常，再验证 RLS 策略 — 发现表启用了 RLS 且仅有默认策略，未开放 `anon` 插入权限。
2. **对比开发/生产环境差异**：本地测试账号有完整权限，Dashboard 手动插入成功，但服务进程以 `anon`（匿名）角色运行被 RLS 拦截。
3. **修复方案选择**：在 SQL Editor 执行 `CREATE POLICY "Allow anon insert" ON hot_topics FOR INSERT TO anon WITH CHECK (true);`（注意 INSERT 用 `WITH CHECK`，`SELECT` 才用 `USING`），后改为直接关闭 RLS（开发阶段）。

**Result（结果）**
数据成功写入 hot_topics 表，前后端联调通过。

**可面试讲的点**：
- "Supabase RLS 与 PostgreSQL RLS 的语法细节"——`INSERT` 策略用 `WITH CHECK` 而非 `USING`
- "排查第三方服务 API 报错的标准思路"——先确认基础连接，再用最小化复现用例定位问题层级
- "开发和生产环境权限模型设计"——`anon` / `authenticated` / `postgres` 角色的区别与选用场景

### 2026-05-26 | LangGraph 异步节点死锁：从同步到异步的艰难迁移

**Situation（背景）**
用 LangGraph 构建了一个 5 节点的 Agent 流水线（outline → content → adapter → quality → rewrite），每个节点都调用 LLM。测试时单个节点正常，但 `ainvoke()` 全流程调用时界面完全卡死，120 秒超时。

**Task（任务）**
定位卡死根因并修复，确保流水线能在 async 上下文中正常运行，同时保持代码可维护性。

**Action（行动）**
1. **分层日志定位**：发现 outline 和 content 生成完成后卡在 quality_checker，而非网络超时。用日志逐步缩小范围，确认是节点调度层面问题。
2. **嵌套事件循环分析**：节点函数是同步的，调用 `client.generate(prompt)` 内部创建 `asyncio.run()`。在 `ainvoke` 的运行中循环内再次 `asyncio.run()` 导致嵌套死锁——子循环抢占了父循环的线程，子循环等待 I/O 时父循环无法调度。
3. **修复路径选择**：方案 A：在线程池执行异步代码；方案 B：把节点改成 async def。优先尝试方案 A（最小改动），但 `run_in_executor` 后主循环仍无法让出。最终采用方案 B——所有节点函数改为 `async def`，`client.generate_async()` 直接 `await`，无嵌套循环。
4. **MiniMax 接入调试**：发现 base_url 用错（`https://api.minimax.chat` → 需加 `/v1` 后缀），导致 API 返回 HTML 而非 JSON。抓包定位后修正。

**Result（结果）**
- 流水线完整运行，选题→大纲→初稿→适配→质检，全流程约 60-80 秒
- `quality_score=7.0` 通过质检，不触发重写
- 所有节点改为 async def，LangGraph 的 `ainvoke` 正确调度

**可面试讲的点**：
- "Python 异步嵌套死锁的排查方法"——用日志缩小范围，识别 `asyncio.run()` 在已有事件循环中的危险性
- "同步代码到异步代码的重构策略"——当库只提供同步接口时，在线程池中用 `asyncio.run()` 创建独立循环
- "LangGraph 节点设计最佳实践"——推荐所有节点用 `async def`，避免调度层面的隐性阻塞