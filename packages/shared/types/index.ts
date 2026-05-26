/**
 * CreatorAgent 共享类型定义
 * 前后端共用
 */

export type Platform = 'xiaohongshu' | 'douyin'

// =====================
// 热点相关类型
// =====================

export interface HotTopic {
  id: string
  title: string
  url: string | null
  platform: Platform
  heat_score: number
  crawled_at: string
}

export type TrendsResponse = ApiResponse<HotTopic[]>

// =====================
// Agent 相关类型
// =====================

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

export type AgentPlatform = 'xiaohongshu' | 'douyin'

export enum AgentNodeStatus {
  Idle = 'idle',
  Running = 'running',
  Done = 'done',
  Error = 'error',
}

// =====================
// 创作者相关类型
// =====================

export interface CreatorProfile {
  id: string
  platform: Platform
  style_vector: number[]
  preferences: Record<string, unknown>
  created_at: string
  updated_at: string
}

// =====================
// 统一 API 响应格式
// =====================

export interface ApiResponse<T> {
  code: number
  data: T | null
  message: string
}

export enum ErrorCode {
  SUCCESS = 0,
  BAD_REQUEST = 4001,
  NOT_FOUND = 4004,
  INTERNAL_ERROR = 5000,
  FIRECRAWL_ERROR = 5001,
  DATABASE_ERROR = 5002,
}

// =====================
// 选题推荐相关类型
// =====================

export interface RecommendRequest {
  keywords: string[]
  user_preferred_tags?: string[]
  platform?: string
  top_k?: number
}