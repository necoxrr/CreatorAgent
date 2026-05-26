"""
Agent 状态定义 — LangGraph StateGraph 的状态 schema
"""
from typing import Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Agent 流水线共享状态

    Attributes:
        topic: 选题内容
        outline: 结构化大纲（outline_generator 输出）
        content: 全文初稿（content_writer 输出）
        adapted_content: 平台适配后内容（style_adapter 输出）
        quality_score: 质检分数（quality_checker 输出）
        rewrite_reason: 修改意见（quality_checker 输出，供 rewrite_agent 使用）
        rewrite_count: 已重写次数（用于限制最多重写2次）
        platform: 目标平台（xiaohongshu / douyin）
        max_rewrites: 最大重写次数上限，默认2
    """

    topic: str = Field(description="选题内容")
    outline: Optional[str] = Field(default=None, description="结构化大纲")
    content: Optional[str] = Field(default=None, description="全文初稿")
    adapted_content: Optional[str] = Field(default=None, description="平台适配后内容")
    quality_score: Optional[float] = Field(default=None, description="质检分数 0-10")
    rewrite_reason: Optional[str] = Field(default=None, description="修改意见")
    rewrite_count: int = Field(default=0, description="已重写次数")
    platform: str = Field(default="xiaohongshu", description="目标平台")
    max_rewrites: int = Field(default=2, description="最大重写次数")

    def should_rewrite(self) -> bool:
        """判断是否需要重写：分数 < 7 且未达上限"""
        if self.quality_score is None:
            return True
        return self.quality_score < 7.0 and self.rewrite_count < self.max_rewrites