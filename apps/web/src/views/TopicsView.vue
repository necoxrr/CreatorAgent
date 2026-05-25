<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">📋 选题推荐</h1>

    <!-- 关键词输入 -->
    <div class="mb-8">
      <div class="flex gap-3 mb-4">
        <input
          v-model="keywordInput"
          type="text"
          placeholder="输入关键词，如：美妆、美食、旅行（点击下方标签可填入）"
          class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          @keyup.enter="addKeyword"
        />
        <button
          @click="addKeyword"
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition"
        >
          添加
        </button>
        <button
          v-if="keywords.length > 0"
          @click="search"
          class="px-6 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition"
        >
          🔍 搜索
        </button>
        <button
          v-if="keywords.length > 0"
          @click="clearKeywords"
          class="px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
        >
          清空
        </button>
      </div>

      <!-- 已选关键词 -->
      <div v-if="keywords.length > 0" class="flex flex-wrap gap-2">
        <span
          v-for="kw in keywords"
          :key="kw"
          class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center gap-1 cursor-pointer hover:bg-primary/20 transition"
          @click="keywordInput = kw"
        >
          {{ kw }}
          <button @click.stop="removeKeyword(kw)" class="hover:text-red-500">×</button>
        </span>
      </div>
    </div>

    <!-- 加载态 -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="h-48 bg-gray-100 rounded-lg animate-pulse" />
    </div>

    <!-- 错误态 -->
    <div v-else-if="error" class="text-center py-20">
      <p class="text-red-500 mb-4">搜索失败: {{ error.message }}</p>
      <button @click="retry" class="px-4 py-2 bg-primary text-white rounded-lg">重试</button>
    </div>

    <!-- 空态 -->
    <div v-else-if="!results.length && hasSearched" class="text-center py-20">
      <p class="text-gray-400 mb-4">未找到相关选题</p>
      <p class="text-sm text-gray-400">尝试其他关键词，或扩大搜索范围</p>
    </div>

    <!-- 无搜索过 -->
    <div v-else-if="!results.length && !hasSearched" class="text-center py-20">
      <p class="text-gray-400">输入关键词开始搜索</p>
    </div>

    <!-- 结果 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="topic in results"
        :key="topic.id"
        class="p-4 border rounded-lg hover:shadow-lg transition cursor-pointer"
      >
        <div class="flex items-start justify-between mb-2">
          <h3 class="font-semibold">{{ topic.title }}</h3>
          <span class="text-xs px-2 py-1 bg-accent/10 text-accent rounded">
            {{ (topic.final_score * 100).toFixed(1) }}%
          </span>
        </div>
        <p v-if="topic.content" class="text-sm text-gray-600 mb-2">{{ topic.content }}</p>
        <div class="flex flex-wrap gap-1 mb-2">
          <span
            v-for="tag in topic.tags"
            :key="tag"
            class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
          >
            {{ tag }}
          </span>
        </div>
        <div class="text-xs text-gray-400 space-x-4">
          <span>🔥 {{ topic.hot_score.toFixed(3) }}</span>
          <span>🎯 {{ topic.style_match.toFixed(2) }}</span>
          <span>⏰ {{ topic.recency_decay.toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRecommendTopics } from '@/composables/useRecommendTopics'

const { results, isLoading, error, recommend } = useRecommendTopics()

const keywordInput = ref('')
const keywords = ref<string[]>([])
const hasSearched = ref(false)

const addKeyword = () => {
  const kw = keywordInput.value.trim()
  if (kw && !keywords.value.includes(kw)) {
    keywords.value.push(kw)
  }
  keywordInput.value = ''
}

const removeKeyword = (kw: string) => {
  keywords.value = keywords.value.filter(k => k !== kw)
}

const clearKeywords = () => {
  keywords.value = []
}

const search = () => {
  if (keywords.value.length === 0) return
  recommend(keywords.value)
  hasSearched.value = true
}

const retry = () => {
  if (keywords.value.length > 0) {
    search()
  }
}
</script>