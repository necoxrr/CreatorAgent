# 🐛 Bug记录

> 格式：| 日期 | #标签 | 症状（≤20字） | 根因 | 修复（≤30字） |

---

## Bug列表
（Claude Code 自动追加）

| 日期 | #标签 | 症状（≤20字） | 根因 | 修复 |
|------|------|-------------|------|------|
| 2026-05-22 | #topic-engine | hot_score全为0 | hot_topics无engagement字段，views=0导致计算得0 | 用heat_score归一化作后备hot_score |
| 2026-05-22 | #topics-api | keywords未参与过滤 | RecommendRequest无keywords字段，且ChromaDB无数据写入 | 添加keywords字段+API层集成ChromaDB+crawler加索引步骤 |
| 2026-05-22 | #API对接 | OpenAI Embedding超时 | 国内网络无法访问OpenAI API | 改用本地sentence-transformers模型 |
| 2026-05-22 | #style-match | style_match恒定0.7 | 无真实用户风格向量数据，always走fallback返回0.7 | 加TODO注释+标注为预留参数 |
| 2026-05-22 | #chroma | dimension mismatch 1536 vs 384 | OpenAI 1536维向量写入，Local 384维读取 | VectorStore 增加 force_recreate=True 参数重建collection |
| 2026-05-22 | #wsl2 | 模型加载多线程死锁 | huggingface 模型加载 WSL2 多线程问题 | --workers 1 启动 uvicorn，模型单例化 |
| 2026-05-22 | #vue | VueQueryPlugin 未注册 | main.ts 未引入 VueQueryPlugin | 补充 app.use(VueQueryPlugin, { queryClient }) |
| 2026-05-22 | #tailwind | secondary 按钮文字看不见 | tailwind.config.js 只配了 DEFAULT 色 | theme.extend.colors 补充 secondary 完整色系 |
| 2026-05-22 | #cors | localhost:5174 请求被拦截 | CORS_ORIGINS 只有 5173/3000 | 追加 5174 到 apps/server/apps/config.py |
| 2026-05-22 | #rls | Supabase 插入数据被拒绝 | hot_topics 表 RLS 阻止 INSERT | 关闭 RLS（RLS disabled），或建 WITH CHECK 策略 |
| 2026-05-22 | #vue-query | Trends 页面数据为空 | useApi.ts interceptor 返回 res.data，但 useQuery 需显式取 .data | 修正 queryFn 显式提取 .data 字段 |