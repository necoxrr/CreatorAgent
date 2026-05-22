export interface Trend {
  id: string
  title: string
  url: string
  platform: 'xiaohongshu' | 'douyin' | 'zhihu'
  heat_score: number
  crawled_at: string
}

export interface TopicRecommendation {
  id: string
  title: string
  content: string
  tags: string[]
  hot_score: number
  style_match: number
  recency_decay: number
  final_score: number
}

export interface AgentState {
  topic: string
  platform: string
  style: string
  outline: string
  draft: string
  final: string
  quality_score: number
  status: 'pending' | 'outline' | 'draft' | 'review' | 'done'
}

export interface ApiResponse<T> {
  code: number
  data: T
  message: string
}