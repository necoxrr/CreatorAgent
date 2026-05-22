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
    keywords: list[str] = []  # 关键词列表，用于语义检索
    user_preferred_tags: list[str] = []  # 用户偏好标签（TODO: 需要真实风格向量训练数据）
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

    - keywords: 关键词列表 → ChromaDB 语义检索（若 collection 有数据）
    - user_preferred_tags: 用户偏好标签 → 用于风格匹配打分（TODO: 需要真实风格向量训练数据）
    - 若 ChromaDB 无数据，则 fallback 到 Supabase 按 heat_score 排序
    """
    try:
        embedder = get_embedder()
        vector_store = get_vector_store()
        topic_engine = get_topic_engine()

        ranked = []

        # 优先用 keywords 做 ChromaDB 语义检索
        if request.keywords:
            query_text = " ".join(request.keywords)
            query_vector = embedder.embed_query(query_text)
            search_results = vector_store.similarity_search(
                query_embedding=query_vector,
                n_results=request.top_k,
                where={"platform": request.platform} if request.platform else None,
            )

            if search_results:
                supabase = get_supabase()
                topic_ids = [r["id"] for r in search_results]
                result = supabase.table("hot_topics").select("*").in_("id", topic_ids).execute()
                topic_dict = {t["id"]: t for t in result.data}

                topics_to_rank = []
                for r in search_results:
                    topic_id = r["id"]
                    if topic_id in topic_dict:
                        topic = topic_dict[topic_id]
                        eng = topic.get("engagement") or {}
                        if not eng or all(v == 0 for v in eng.values()):
                            heat = topic.get("heat_score") or 0
                            eng = {"views": heat, "likes": 0, "comments": 0, "shares": 0}
                        # 注入 ChromaDB 语义相似度 distance 作为额外排序因子
                        distance = r.get("distance") or 1.0
                        similarity_score = max(0.0, 1.0 - distance / 2.0)  # 归一化到 [0,1]
                        topics_to_rank.append({
                            "id": topic["id"],
                            "title": topic.get("title", ""),
                            "content": r["document"],
                            "tags": topic.get("tags", []),
                            "published_at": topic.get("published_at"),
                            "engagement": eng,
                            "similarity": similarity_score,  # 额外的语义相似度分数
                        })

                ranked = topic_engine.rank_topics(
                    topics=topics_to_rank,
                    user_preferred_tags=request.user_preferred_tags,
                    top_n=request.top_k,
                )
            # ChromaDB 为空则 fallback 到 Supabase

        # Fallback / 无 keywords 时直接查 Supabase
        if not ranked:
            supabase = get_supabase()
            query = supabase.table("hot_topics").select("*")
            if request.platform:
                query = query.eq("platform", request.platform)
            result = query.order("heat_score", desc=True).limit(request.top_k).execute()

            topics_data = []
            for t in result.data:
                heat = t.get("heat_score") or 0
                eng = t.get("engagement") or {}
                if not eng or all(v == 0 for v in eng.values()):
                    eng = {"views": heat, "likes": 0, "comments": 0, "shares": 0}
                topics_data.append({
                    "id": t["id"],
                    "title": t.get("title", ""),
                    "content": t.get("content", ""),
                    "tags": t.get("tags", []),
                    "published_at": t.get("published_at"),
                    "engagement": eng,
                })

            ranked = topic_engine.rank_topics(
                topics=topics_data,
                user_preferred_tags=request.user_preferred_tags,
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