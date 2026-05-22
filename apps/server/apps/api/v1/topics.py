"""
选题推荐 API 路由
POST /api/v1/topics/recommend - 获取选题推荐
"""
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from ...db.supabase import get_supabase
from ...rag.vector_store import get_vector_store
from ...rag.embedder import get_embedder
from ...rag.topic_engine import get_topic_engine, TopicScore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/topics", tags=["选题推荐"])


class RecommendRequest(BaseModel):
    """选题推荐请求"""
    user_preferred_tags: list[str] = []
    platform: Optional[str] = None
    top_k: int = Query(default=10, ge=1, le=50, description="返回数量")


class TopicItem(BaseModel):
    """选题项"""
    id: str
    title: str
    content: str
    tags: list[str]
    hot_score: float
    style_match: float
    recency_decay: float
    final_score: float


class RecommendResponse(BaseModel):
    """选题推荐响应"""
    topics: list[TopicItem]
    total: int


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_topics(
    request: RecommendRequest,
) -> RecommendResponse:
    """
    获取个性化选题推荐

    基于用户偏好标签，从已索引的选题库中检索并排序
    """
    try:
        # 初始化组件
        embedder = get_embedder()
        vector_store = get_vector_store()
        topic_engine = get_topic_engine()

        # 如果有用户偏好标签，先进行向量检索
        if request.user_preferred_tags:
            # 将用户偏好转换为查询向量（异步）
            preference_text = " ".join(request.user_preferred_tags)
            query_vector = await embedder.embed_query(preference_text)

            # 语义检索（同步）
            search_results = vector_store.similarity_search(
                query_embedding=query_vector,
                n_results=request.top_k,
                where={"platform": request.platform} if request.platform else None,
            )

            # 获取原始选题数据
            if search_results:
                supabase = get_supabase()
                topic_ids = [r["id"] for r in search_results]
                result = supabase.table("hot_topics").select("*").in_("id", topic_ids).execute()

                # 构造成字典便于查找
                topic_dict = {t["id"]: t for t in result.data}

                # 使用 topic_engine 排序
                topics_to_rank = []
                for r in search_results:
                    topic_id = r["id"]
                    if topic_id in topic_dict:
                        topic = topic_dict[topic_id]
                        topics_to_rank.append({
                            "id": topic["id"],
                            "title": topic.get("title", ""),
                            "content": r["document"],
                            "tags": topic.get("tags", []),
                            "published_at": topic.get("published_at"),
                            "engagement": topic.get("engagement", {}),
                        })

                ranked = topic_engine.rank_topics(
                    topics=topics_to_rank,
                    user_preferred_tags=request.user_preferred_tags,
                    top_n=request.top_k,
                )
            else:
                ranked = []
        else:
            # 无偏好时，直接从数据库获取最新热题
            supabase = get_supabase()
            query = supabase.table("hot_topics").select("*")

            if request.platform:
                query = query.eq("platform", request.platform)

            result = query.order("heat_score", desc=True).limit(request.top_k).execute()

            ranked = topic_engine.rank_topics(
                topics=[
                    {
                        "id": t["id"],
                        "title": t.get("title", ""),
                        "content": t.get("content", ""),
                        "tags": t.get("tags", []),
                        "published_at": t.get("published_at"),
                        "engagement": t.get("engagement", {}),
                    }
                    for t in result.data
                ],
                user_preferred_tags=[],
                top_n=request.top_k,
            )

        # 转换为响应格式
        topics = [
            TopicItem(
                id=s.topic_id,
                title=s.title,
                content=s.content,
                tags=[],  # 从数据库获取
                hot_score=s.hot_score,
                style_match=s.style_match,
                recency_decay=s.recency_decay,
                final_score=s.final_score,
            )
            for s in ranked
        ]

        return RecommendResponse(topics=topics, total=len(topics))

    except Exception as e:
        logger.error(f"选题推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))