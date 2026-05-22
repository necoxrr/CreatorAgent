import { ref } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import { topicsApi } from '@/api/client'
import type { TopicRecommendation } from '@/types'

export function useRecommendTopics() {
  const results = ref<TopicRecommendation[]>([])
  const keywords = ref<string[]>([])

  const { mutate, isPending, error } = useMutation({
    mutationFn: async (params: { keywords: string[]; user_preferred_tags?: string[]; platform?: string }) => {
      const res = await topicsApi.recommend(params)
      return res as unknown as { topics: TopicRecommendation[]; total: number }
    },
    onSuccess: (data) => {
      results.value = data.topics
    }
  })

  const recommend = (kw: string[], tags?: string[], platform?: string) => {
    mutate({ keywords: kw, user_preferred_tags: tags, platform })
  }

  return {
    results,
    keywords,
    isLoading: isPending,
    error,
    recommend
  }
}