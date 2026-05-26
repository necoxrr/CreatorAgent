@rules.md @skills/agent-builder.md

本周核心：用LangGraph搭建多节点Agent流水线。

1. 定义AgentState（shared types同步前后端）
2. 创建5个Agent节点：
   - outline_generator.py — 选题→结构化大纲
   - content_writer.py — 大纲→全文初稿
   - style_adapter.py — 初稿→平台适配
   - quality_checker.py — 评分+修改意见
   - rewrite_agent.py — 根据意见重写
3. graph.py 组装StateGraph，含条件分支（quality<7→重写，最多2次）
4. API `POST /api/v1/agent/generate`
5. 前端React Flow工作流可视化

每完成一个节点就写测试验证，不要等5个一起写。


---

## ⚠️ 实战踩坑（Claude Code 执行后自动追加）

> 格式：| 日期 | 问题（≤20字） | 解决（≤30字） | #标签 |

| 2026-05-26 | AgentState multiple values | 改用 new_state = state.model_dump() 后赋值再构造 | #agent |
| 2026-05-26 | 节点内 asyncio.run 死锁 | 同步函数改为 async def + generate_async | #agent |
| 2026-05-26 | MiniMax base_url 缺 /v1 | 改为 https://api.minimax.chat/v1 | #minimax |
| 2026-05-26 | rewrite_count 变字符串 | 显式 int() 转换 | #agent |
