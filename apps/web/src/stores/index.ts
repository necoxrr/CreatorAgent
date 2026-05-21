import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const currentPlatform = ref<'xiaohongshu' | 'douyin'>('xiaohongshu')
  return { currentPlatform }
})