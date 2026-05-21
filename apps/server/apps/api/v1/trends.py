"""
热点话题 API 路由
GET /api/v1/trends - 获取热点列表
POST /api/v1/trends/refresh - 手动触发抓取
"""
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from ...db.supabase import get_supabase
from ...models.schemas import HotTopicResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/trends", tags=["热点"])


@router.get("/")
async def get_trends(
    platform: Optional[str] = Query(None, description="平台过滤: xiaohongshu | douyin"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
) -> dict:
    """
    获取热点话题列表

    按热度降序排列，支持平台过滤
    """
    try:
        supabase = get_supabase()
        query = supabase.table("hot_topics").select("*")

        if platform:
            query = query.eq("platform", platform)

        result = query.order("heat_score", desc=True).limit(limit).execute()

        return {"code": 0, "data": result.data, "message": "ok"}
    except Exception as e:
        logger.error(f"获取热点列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_trends() -> dict:
    """
    手动触发热搜抓取

    抖音使用免费 API，小红书需要 FIRECRAWL_API_KEY
    """
    try:
        from ...crawler.douyin_client import DouyinClient
        from ...crawler.scheduler import crawl_and_save

        platforms = ["xiaohongshu", "douyin"]
        total = 0

        for platform in platforms:
            count = await crawl_and_save(platform)
            total += count

        return {"code": 0, "data": {"total": total}, "message": f"抓取完成，共{total}条"}
    except Exception as e:
        logger.error(f"触发抓取失败: {e}")
        return {"code": 5001, "data": None, "message": str(e)}
