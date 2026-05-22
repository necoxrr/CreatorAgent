import { useQuery } from '@tanstack/vue-query'
import api from '@/api/client'
import type { Trend } from '@/types'

export function useGetTrends() {
  return useQuery<Trend[]>({
    queryKey: ['trends'],
    queryFn: async () => {
      const res = await api.get('/api/v1/trends')
      return (res as unknown as { code: number; data: Trend[]; message: string }).data
    }
  })
}