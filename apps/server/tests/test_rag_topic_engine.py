"""
TopicEngine 模块测试
"""
import pytest
from datetime import datetime, timedelta
from apps.rag.topic_engine import TopicEngine, TopicScore


class TestTopicEngine:
    """TopicEngine 测试"""

    @pytest.fixture
    def engine(self):
        """创建 TopicEngine 实例"""
        return TopicEngine(decay_half_life_days=7)

    def test_calculate_recency_decay_fresh(self, engine):
        """新鲜内容衰减测试"""
        now = datetime.now()
        recent = (now - timedelta(days=1)).isoformat()
        decay = engine.calculate_recency_decay(recent)
        assert decay > 0.9  # 1天前应该衰减很少

    def test_calculate_recency_decay_old(self, engine):
        """老内容衰减测试"""
        old = (datetime.now() - timedelta(days=14)).isoformat()
        decay = engine.calculate_recency_decay(old)
        assert decay < 0.5  # 14天前应该衰减到一半以下

    def test_calculate_recency_decay_none(self, engine):
        """无时间信息测试"""
        decay = engine.calculate_recency_decay(None)
        assert decay == 0.5

    def test_calculate_style_match_perfect(self, engine):
        """完美匹配测试"""
        tags = ["美妆", "护肤", "教程"]
        preferred = ["美妆", "护肤", "教程"]
        match = engine.calculate_style_match(tags, preferred)
        assert match == 1.0

    def test_calculate_style_match_partial(self, engine):
        """部分匹配测试"""
        tags = ["美妆", "护肤", "教程"]
        preferred = ["美妆", "穿搭"]
        match = engine.calculate_style_match(tags, preferred)
        assert 0 < match < 1

    def test_calculate_style_match_no_preference(self, engine):
        """无偏好测试"""
        tags = ["美妆"]
        match = engine.calculate_style_match(tags, [])
        assert match == 0.7  # 默认值

    def test_calculate_hot_score_high(self, engine):
        """高热度测试"""
        engagement = {"views": 100000, "likes": 5000, "comments": 200, "shares": 100}
        score = engine.calculate_hot_score(engagement)
        assert score > 0.5

    def test_calculate_hot_score_low(self, engine):
        """低热度测试"""
        engagement = {"views": 100, "likes": 5, "comments": 0, "shares": 0}
        score = engine.calculate_hot_score(engagement)
        assert score < 0.5  # 低浏览量应该分数较低

    def test_calculate_hot_score_zero_views(self, engine):
        """零浏览量测试"""
        engagement = {"views": 0, "likes": 0, "comments": 0, "shares": 0}
        score = engine.calculate_hot_score(engagement)
        assert score == 0.0

    def test_score_topic(self, engine):
        """综合打分测试"""
        score = engine.score_topic(
            topic_id="1",
            title="测试标题",
            content="测试内容",
            topic_tags=["美妆"],
            published_at=(datetime.now() - timedelta(days=2)).isoformat(),
            engagement={"views": 50000, "likes": 2000, "comments": 100, "shares": 50},
            user_preferred_tags=["美妆", "护肤"],
        )
        assert isinstance(score, TopicScore)
        assert score.final_score > 0
        assert 0 <= score.hot_score <= 1
        assert 0 <= score.style_match <= 1
        assert 0 <= score.recency_decay <= 1

    def test_rank_topics(self, engine):
        """排序测试"""
        topics = [
            {
                "id": "1",
                "title": "热门",
                "content": "内容1",
                "tags": ["美妆"],
                "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "engagement": {"views": 100000, "likes": 5000, "comments": 200, "shares": 100},
            },
            {
                "id": "2",
                "title": "冷门",
                "content": "内容2",
                "tags": ["科技"],
                "published_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "engagement": {"views": 100, "likes": 5, "comments": 0, "shares": 0},
            },
        ]
        ranked = engine.rank_topics(topics, user_preferred_tags=["美妆"], top_n=2)
        assert len(ranked) == 2
        assert ranked[0].topic_id == "1"  # 热门应该排第一