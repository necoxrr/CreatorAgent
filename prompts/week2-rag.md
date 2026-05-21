@rules.md @skills/fastapi-craft.md

本周核心：构建RAG检索 + 选题推荐引擎。

1. `apps/server/rag/embedder.py` — Embedding模块
   - OpenAI text-embedding-3-small，封装分块+向量化
2. `apps/server/rag/vector_store.py` — ChromaDB操作
   - 初始化collection、批量写入、语义检索top_k=10
3. `apps/server/rag/topic_engine.py` — 选题推荐引擎
   - 热点向量 × 风格匹配度 × 时效衰减 → 综合打分
4. API接口 `POST /api/v1/topics/recommend`
5. 前端选题推荐页

每个模块写完给测试case。


---

## ⚠️ 实战踩坑（Claude Code 执行后自动追加）

> 格式：| 日期 | 问题（≤20字） | 解决（≤30字） | #标签 |
