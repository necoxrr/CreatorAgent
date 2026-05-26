<script setup lang="ts">
/**
 * Agent 工作流可视化页面
 * 基于 Vue Flow 展示 LangGraph Agent 流水线的执行状态
 */
import { ref, computed, onMounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import { agentApi } from '@/api/client'

// 选题输入
const topic = ref('')
const platform = ref('xiaohongshu')

// 工作流节点定义（静态）
const nodes = ref([
  {
    id: '1',
    label: '📝 选题',
    style: { background: '#f3f4f6', padding: '12px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }
  },
  {
    id: '2',
    label: '📋 大纲生成',
    style: { background: '#eff6ff', padding: '12px', borderRadius: '8px', border: '1px solid #bfdbfe', fontSize: '14px' }
  },
  {
    id: '3',
    label: '✍️ 内容初稿',
    style: { background: '#f0fdf4', padding: '12px', borderRadius: '8px', border: '1px solid #bbf7d0', fontSize: '14px' }
  },
  {
    id: '4',
    label: '🎯 平台适配',
    style: { background: '#fef3c7', padding: '12px', borderRadius: '8px', border: '1px solid #fde68a', fontSize: '14px' }
  },
  {
    id: '5',
    label: '🔍 质检评分',
    style: { background: '#fdf4f7', padding: '12px', borderRadius: '8px', border: '1px solid #fbcfe8', fontSize: '14px' }
  },
  {
    id: '6',
    label: '🔄 重写',
    style: { background: '#fee2e2', padding: '12px', borderRadius: '8px', border: '1px solid #fca5a5', fontSize: '14px' }
  },
  {
    id: '7',
    label: '✅ 完成',
    style: { background: '#dcfce7', padding: '12px', borderRadius: '8px', border: '1px solid #86efac', fontSize: '14px' }
  }
])

// 工作流边定义
const edges = ref([
  { id: 'e1-2', source: '1', target: '2', animated: false, type: 'smoothstep' },
  { id: 'e2-3', source: '2', target: '3', animated: false, type: 'smoothstep' },
  { id: 'e3-4', source: '3', target: '4', animated: false, type: 'smoothstep' },
  { id: 'e4-5', source: '4', target: '5', animated: false, type: 'smoothstep' },
  { id: 'e5-6', source: '5', target: '6', label: 'quality < 7', type: 'smoothstep', style: { stroke: '#ef4444' } },
  { id: 'e5-7', source: '5', target: '7', label: 'quality >= 7', type: 'smoothstep', style: { stroke: '#22c55e' } },
  { id: 'e6-4', source: '6', target: '4', label: '重新适配', type: 'smoothstep', style: { stroke: '#f97316' }, animated: true }
])

// 当前活跃节点
const activeNodeId = ref<string | null>(null)

// 生成状态
const isGenerating = ref(false)
const error = ref<string | null>(null)

// 生成结果
const result = ref<{
  outline: string | null
  content: string | null
  adapted_content: string | null
  quality_score: number | null
  rewrite_count: number
} | null>(null)

// 节点位置配置
const nodePositions = [
  { id: '1', position: { x: 250, y: 0 } },
  { id: '2', position: { x: 250, y: 100 } },
  { id: '3', position: { x: 250, y: 200 } },
  { id: '4', position: { x: 250, y: 300 } },
  { id: '5', position: { x: 250, y: 400 } },
  { id: '6', position: { x: 50, y: 500 } },
  { id: '7', position: { x: 250, y: 500 } }
]

// 节点 ID 映射
const nodeIdMap: Record<string, string> = {
  outline: '2',
  content: '3',
  adapted: '4',
  quality: '5',
  rewrite: '6',
  done: '7'
}

// 高亮对应节点
function highlightNode(nodeId: string) {
  activeNodeId.value = nodeId
  // 更新边的动画状态
  edges.value = edges.value.map(e => {
    if (e.source === activeNodeId.value) {
      return { ...e, animated: true }
    }
    return { ...e, animated: false }
  })
}

// 重置高亮
function resetHighlight() {
  activeNodeId.value = null
  edges.value = edges.value.map(e => ({ ...e, animated: false }))
}

// 触发生成
async function generate() {
  if (!topic.value.trim()) return

  isGenerating.value = true
  error.value = null
  result.value = null
  resetHighlight()

  try {
    // 选题 → 大纲
    highlightNode('2')

    const res = await agentApi.generate({
      topic: topic.value,
      platform: platform.value,
      max_rewrites: 2
    })

    result.value = res

    // 根据结果高亮最终节点
    if (res.quality_score !== null && res.quality_score >= 7) {
      highlightNode('7')
    } else {
      highlightNode('6')
    }
  } catch (e: any) {
    error.value = e.message || '生成失败'
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">🤖 Agent 工作流</h1>

    <!-- 输入区域 -->
    <div class="mb-8 bg-white rounded-xl shadow-sm p-6">
      <div class="flex flex-wrap gap-4 mb-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">选题内容</label>
          <input
            v-model="topic"
            type="text"
            placeholder="输入你要创作的主题，例如：夏天必备的美妆好物"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            :disabled="isGenerating"
            @keyup.enter="!isGenerating && generate()"
            data-testid="topic-input"
          />
        </div>
        <div class="w-40">
          <label class="block text-sm font-medium text-gray-700 mb-1">平台</label>
          <select
            v-model="platform"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            :disabled="isGenerating"
          >
            <option value="xiaohongshu">小红书</option>
            <option value="douyin">抖音</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="generate"
            :disabled="isGenerating || !topic.trim()"
            class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="generate-btn"
          >
            {{ isGenerating ? '生成中...' : '🚀 开始生成' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 工作流可视化 -->
    <div class="mb-8 bg-white rounded-xl shadow-sm p-4">
      <h2 class="text-lg font-semibold mb-4">流水线状态</h2>
      <div class="h-[500px] border rounded-lg">
        <VueFlow
          :nodes="nodes.map(n => ({
            id: n.id,
            position: nodePositions.find(p => p.id === n.id)?.position || { x: 0, y: 0 },
            data: { label: n.label },
            style: {
              ...n.style,
              opacity: activeNodeId && activeNodeId !== n.id ? 0.5 : 1,
              boxShadow: activeNodeId === n.id ? '0 0 20px rgba(59,130,246,0.5)' : 'none'
            }
          }))"
          :edges="edges.map(e => ({
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.label,
            type: e.type,
            animated: e.animated,
            style: e.style
          }))"
          :fit-view-on-init="true"
          :zoom="1.2"
        >
          <Background pattern-color="#e5e7eb" :gap="16" />
          <Controls />
        </VueFlow>
      </div>

      <!-- 流水线说明 -->
      <div class="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-blue-100 border border-blue-300"></span>
          待处理
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-primary"></span>
          执行中
        </span>
        <span class="flex items-center gap-1">
          <span class="w-3 h-3 rounded-full bg-green-100 border border-green-300"></span>
          完成
        </span>
      </div>
    </div>

    <!-- 生成结果 -->
    <div v-if="error" class="mb-8 bg-red-50 border border-red-200 rounded-xl p-6" data-testid="error-state">
      <p class="text-red-600">生成失败: {{ error }}</p>
    </div>

    <div v-else-if="result" class="grid grid-cols-1 lg:grid-cols-2 gap-6" data-testid="result-content">
      <!-- 大纲 -->
      <div v-if="result.outline" class="bg-white rounded-xl shadow-sm p-6" data-testid="outline-result">
        <h3 class="font-semibold mb-3">📋 生成大纲</h3>
        <pre class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">{{ result.outline }}</pre>
      </div>

      <!-- 初稿 -->
      <div v-if="result.content" class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-semibold mb-3">✍️ 内容初稿</h3>
        <p class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">{{ result.content }}</p>
      </div>

      <!-- 适配后内容 -->
      <div v-if="result.adapted_content" class="bg-white rounded-xl shadow-sm p-6 lg:col-span-2">
        <h3 class="font-semibold mb-3">🎯 平台适配内容</h3>
        <p class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg overflow-auto max-h-80">{{ result.adapted_content }}</p>
      </div>

      <!-- 质检结果 -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-semibold mb-3">🔍 质检评分</h3>
        <div class="flex items-center gap-4">
          <div class="text-4xl font-bold" :class="result.quality_score !== null && result.quality_score >= 7 ? 'text-green-600' : 'text-orange-600'">
            {{ result.quality_score !== null ? result.quality_score.toFixed(1) : 'N/A' }}
            <span class="text-lg text-gray-400">/ 10</span>
          </div>
          <div class="text-sm text-gray-600">
            <p>重写次数: {{ result.rewrite_count }}</p>
            <p>状态: {{ result.quality_score !== null && result.quality_score >= 7 ? '✅ 通过' : '⚠️ 需优化' }}</p>
          </div>
        </div>
        <!-- 评分进度条 -->
        <div class="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="result.quality_score !== null && result.quality_score >= 7 ? 'bg-green-500' : 'bg-orange-500'"
            :style="{ width: `${(result.quality_score ?? 0) * 10}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>