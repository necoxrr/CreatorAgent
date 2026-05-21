"""
Pydantic 模型定义
用于 API 请求/响应数据校验
"""
from pydantic import BaseModel, Field
from typing import Optional


class HotTopicBase(BaseModel):
    """热点话题基础模型"""
    title: str = Field(..., description="话题标题")
    url: Optional[str] = Field(None, description="话题链接")
    platform: str = Field(..., description="平台: xiaohongshu | douyin")
    heat_score: int = Field(0, description="热度分值")


class HotTopicCreate(HotTopicBase):
    """创建热点话题"""
    pass


class HotTopicResponse(HotTopicBase):
    """热点话题响应"""
    id: str
    crawled_at: str

    class Config:
        from_attributes = True


class TrendsQuery(BaseModel):
    """热点列表查询参数"""
    platform: Optional[str] = Field(None, description="平台过滤")
    limit: int = Field(20, ge=1, le=100, description="返回数量")


class ApiSuccessResponse(BaseModel):
    """成功响应"""
    code: int = 0
    data: dict | list | None = None
    message: str = "ok"


class ApiErrorResponse(BaseModel):
    """错误响应"""
    code: int
    data: None = None
    message: str
