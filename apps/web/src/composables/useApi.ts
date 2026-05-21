import { useQuery } from '@tanstack/vue-query'
import api from '@/api/client'
import type { Trend } from '@/types'

export function useGetTrends() {
  return useQuery<Trend[]>({
    queryKey: ['trends'],
    queryFn: async () => {
      return await api.get('/api/v1/trends') as unknown as Trend[]
    }
  })
}