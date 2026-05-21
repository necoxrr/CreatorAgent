<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">🔥 热点发现</h1>
    <div v-if="isLoading" data-testid="skeleton" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="h-48 bg-gray-100 rounded-lg animate-pulse" />
    </div>
    <div v-else-if="error" data-testid="error-state" class="text-center py-20">
      <p class="text-red-500 mb-4">加载失败</p>
      <button @click="() => refetch()" class="px-4 py-2 bg-primary text-white rounded-lg">重试</button>
    </div>
    <div v-else-if="!trends?.length" data-testid="empty-state" class="text-center py-20">
      <p class="text-gray-400">暂无热点数据</p>
    </div>
    <div v-else data-testid="content" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in trends" :key="item.id" class="p-4 border rounded-lg hover:shadow-lg transition cursor-pointer">
        <span class="text-xs px-2 py-1 bg-primary/10 text-primary rounded">{{ item.platform }}</span>
        <h3 class="font-semibold mt-2">{{ item.title }}</h3>
        <p class="text-sm text-gray-500 mt-1">热度 {{ item.heat_score }}</p>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useGetTrends } from '@/composables/useApi'

const { data: trends, isLoading, error, refetch } = useGetTrends()
</script>