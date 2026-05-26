import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 180000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  res => {
    const { code, message } = res.data ?? {}
    if (code !== undefined && code !== 0) throw new Error(message ?? '请求失败')
    return res.data
  },
  err => Promise.reject(err)
)

export interface RecommendRequest {
  keywords: string[]
  user_preferred_tags?: string[]
  platform?: string
  top_k?: number
}

export const topicsApi = {
  recommend(params: RecommendRequest) {
    return api.post('/api/v1/topics/recommend', params)
  }
}

export interface GenerateRequest {
  topic: string
  platform?: string
  max_rewrites?: number
}

export interface GenerateResponse {
  outline: string | null
  content: string | null
  adapted_content: string | null
  quality_score: number | null
  rewrite_count: number
}

export const agentApi = {
  generate(params: GenerateRequest): Promise<GenerateResponse> {
    return api.post('/api/v1/agent/generate', params)
  }
}

export default api