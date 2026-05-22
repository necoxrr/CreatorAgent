"""
选题推荐引擎
热点向量 × 风格匹配度 × 时效衰减 → 综合打分
"""
import logging
import math
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 时效衰减配置
RECENCY_DECAY_HALF_LIFE_DAYS = 7  # 半衰期 7 天


@dataclass
class TopicScore:
    """选题打分结果"""
    topic_id: str
    title: str
    content: str
    hot_score: float  # 热点分数 (0-1)
    style_match: float  # 风格匹配度 (0-1)
    recency_decay: float  # 时效衰减 (0-1)
    final_score: float  # 综合分数


class TopicEngine:
    """选题推荐引擎"""

    def __init__(self, decay_half_life_days: int = RECENCY_DECAY_HALF_LIFE_DAYS):
        self.decay_half_life_days = decay_half_life_days

    def calculate_recency_decay(self, published_at: Optional[str]) -> float:
        """
        计算时效衰减因子

        Args:
            published_at: 发布时间 ISO 格式

        Returns:
            衰减因子 (0-1，越新越接近1)
        """
        if not published_at:
            return 0.5  # 无时间信息，默认中间值

        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            now = datetime.now(dt.tzinfo)
            days_elapsed = (now - dt).days

            # 指数衰减: e^(-λt), 其中半衰期 λ = ln(2)/half_life
            half_life = self.decay_half_life_days
            decay = math.exp(-0.693 * days_elapsed / half_life)
            return max(0.1, min(1.0, decay))  # 限制在 [0.1, 1.0]
        except Exception as e:
            logger.warning(f"Failed to parse date {published_at}: {e}")
            return 0.5

    def calculate_style_match(
        self,
        topic_tags: list[str],
        user_preferred_tags: list[str],
    ) -> float:
        """
        计算风格匹配度

        Args:
            topic_tags: 选题标签
            user_preferred_tags: 用户偏好标签

        Returns:
            匹配度 (0-1)

        TODO: 当前为 Jaccard 文本匹配，需要真实用户风格向量训练数据才能生效。
              style_profile_id 参数预留，待风格画像模型训练完成后启用。
        """
        if not user_preferred_tags:
            return 0.7  # 无偏好时默认

        if not topic_tags:
            return 0.3  # 无标签时低匹配

        # Jaccard 相似度
        topic_set = set(topic_tags)
        preferred_set = set(user_preferred_tags)
        intersection = len(topic_set & preferred_set)
        union = len(topic_set | preferred_set)

        if union == 0:
            return 0.3

        return intersection / union

    def calculate_hot_score(self, engagement: dict) -> float:
        """
        计算热点分数

        Args:
            engagement: 互动数据 (likes, comments, shares, views)

        Returns:
            热点分数 (0-1)
        """
        views = engagement.get("views", 0)
        likes = engagement.get("likes", 0)
        comments = engagement.get("comments", 0)
        shares = engagement.get("shares", 0)

        if views == 0:
            return 0.0

        # 互动率 = (点赞 + 评论 * 2 + 分享 * 3) / 浏览量
        engagement_rate = (likes + comments * 2 + shares * 3) / views

        # 热度分数：互动率 × 浏览量权重
        # 浏览量越高，基础分数越高
        view_score = min(math.log10(max(views, 1) + 1) / 10, 1.0)  # 最多 1e10 曝光对应 1.0
        engagement_score = min(engagement_rate * 10, 1.0)  # 10% 互动率对应 1.0

        # 综合：曝光权重 40%，互动质量 60%
        hot_score = view_score * 0.4 + engagement_score * 0.6
        return max(0.0, min(1.0, hot_score))

    def score_topic(
        self,
        topic_id: str,
        title: str,
        content: str,
        topic_tags: list[str],
        published_at: Optional[str],
        engagement: dict,
        user_preferred_tags: list[str],
        similarity: float = 1.0,
    ) -> TopicScore:
        """
        综合打分

        Args:
            similarity: ChromaDB 语义相似度分数 (0-1)，用于加权排序
        """
        hot_score = self.calculate_hot_score(engagement)
        style_match = self.calculate_style_match(topic_tags, user_preferred_tags)
        recency_decay = self.calculate_recency_decay(published_at)

        # 综合分数 = 热点 × 风格匹配 × 时效衰减 × 语义相似度（若无可用相似度则为1.0）
        final_score = hot_score * style_match * recency_decay * similarity

        return TopicScore(
            topic_id=topic_id,
            title=title,
            content=content,
            hot_score=hot_score,
            style_match=style_match,
            recency_decay=recency_decay,
            final_score=final_score,
        )

    def rank_topics(
        self,
        topics: list[dict],
        user_preferred_tags: list[str],
        top_n: int = 10,
    ) -> list[TopicScore]:
        """
        对选题列表排序

        Args:
            topics: 选题列表，每个 dict 包含 id, title, content, tags, published_at, engagement
            user_preferred_tags: 用户偏好标签
            top_n: 返回前 N 个

        Returns:
            排序后的 TopicScore 列表
        """
        scored_topics = []

        for topic in topics:
            score = self.score_topic(
                topic_id=topic.get("id", ""),
                title=topic.get("title", ""),
                content=topic.get("content", ""),
                topic_tags=topic.get("tags", []),
                published_at=topic.get("published_at"),
                engagement=topic.get("engagement", {}),
                user_preferred_tags=user_preferred_tags,
                similarity=topic.get("similarity", 1.0),
            )
            scored_topics.append(score)

        # 按综合分数降序排列
        scored_topics.sort(key=lambda x: x.final_score, reverse=True)

        return scored_topics[:top_n]


def get_topic_engine() -> TopicEngine:
    """获取 TopicEngine 实例"""
    return TopicEngine()