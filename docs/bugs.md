# 🐛 Bug记录

> 格式：| 日期 | #标签 | 症状（≤20字） | 根因 | 修复（≤30字） |

---

## Bug列表
（Claude Code 自动追加）

| 日期 | #标签 | 症状（≤20字） | 根因 | 修复 |
|------|------|-------------|------|------|
| 2026-05-22 | #topic-engine | hot_score 全为0 | hot_topics无engagement字段，views=0导致直接返回0 | 用heat_score归一化作后备hot_score |
| 2026-05-22 | #topics-api | keywords未参与过滤 | RecommendRequest无keywords字段，且ChromaDB无数据写入 | 添加keywords字段+API层集成ChromaDB+crawler加索引步骤 |
| 2026-05-22 | #API对接 | OpenAI Embedding API国内超时 | 改用本地sentence-transformers模型 |
| 2026-05-22 | #style-match | style_match恒定0.7 | 无真实用户风格向量数据，always走fallback | 加TODO注释+标注为预留参数 |