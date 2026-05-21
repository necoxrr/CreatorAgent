/**
 * CreatorAgent 共享类型定义
 * 前后端共用
 */

export type Platform = 'xiaohongshu' | 'douyin'

/**
 * 热点话题
 */
export interface HotTopic {
  id: string
  title: string
  url: string | null
  platform: Platform
  heat_score: number
  crawled_at: string
}

/**
 * 创作者画像
 */
export interface CreatorProfile {
  id: string
  platform: Platform
  style_vector: number[]
  preferences: Record<string, unknown>
  created_at: string
  updated_at: string
}

/**
 * 统一 API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  data: T | null
  message: string
}

/**
 * 热点列表响应
 */
export type TrendsResponse = ApiResponse<HotTopic[]>

/**
 * 错误码定义
 */
export enum ErrorCode {
  SUCCESS = 0,
  BAD_REQUEST = 4001,
  NOT_FOUND = 4004,
  INTERNAL_ERROR = 5000,
  FIRECRAWL_ERROR = 5001,
  DATABASE_ERROR = 5002,
}
