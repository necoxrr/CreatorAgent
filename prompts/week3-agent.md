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
