@rules.md @skills/vue-ui.md

本周核心：文案编辑器 + 数据仪表盘。

1. 编辑器页 `apps/web/src/views/EditorView.vue`
   - 左侧：Markdown编辑区（实时预览切换）
   - 右侧：AI面板（大纲/续写/风格切换/标题生成）
   - AI处理中显示流式输出动画
2. 仪表盘 `apps/web/src/views/DashboardView.vue`
   - 顶部：三个统计卡片
   - 中间：ECharts热点趋势折线图（近30天）
   - 底部：风格雷达图（五维）
3. 数据从 `/api/v1/analytics/*` 接口拿

先做编辑器再搞仪表盘。


---

## ⚠️ 实战踩坑（Claude Code 执行后自动追加）

> 格式：| 日期 | 问题（≤20字） | 解决（≤30字） | #标签 |
