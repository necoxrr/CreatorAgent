"""
Agent State 单元测试
"""
import pytest
from apps.agent.state import AgentState


class TestAgentState:
    """AgentState 行为测试"""

    def test_should_rewrite_when_score_below_7_and_count_less_than_max(self):
        """quality < 7 且未达上限时，应该重写"""
        state = AgentState(
            topic="测试选题",
            quality_score=5.0,
            rewrite_count=0,
            max_rewrites=2,
        )
        assert state.should_rewrite() is True

    def test_should_not_rewrite_when_score_above_7(self):
        """quality >= 7 时，不应重写"""
        state = AgentState(
            topic="测试选题",
            quality_score=8.0,
            rewrite_count=0,
            max_rewrites=2,
        )
        assert state.should_rewrite() is False

    def test_should_not_rewrite_when_max_rewrites_reached(self):
        """已重写次数达到上限时，不应重写"""
        state = AgentState(
            topic="测试选题",
            quality_score=5.0,
            rewrite_count=2,
            max_rewrites=2,
        )
        assert state.should_rewrite() is False

    def test_should_rewrite_when_score_below_7_at_second_last_rewrite(self):
        """quality < 7，第2次重写（最后一次）应该继续"""
        state = AgentState(
            topic="测试选题",
            quality_score=5.0,
            rewrite_count=1,
            max_rewrites=2,
        )
        assert state.should_rewrite() is True

    def test_should_rewrite_when_score_is_none(self):
        """quality_score 未设置时，应该重写（安全默认值）"""
        state = AgentState(
            topic="测试选题",
            quality_score=None,
            rewrite_count=0,
            max_rewrites=2,
        )
        assert state.should_rewrite() is True

    def test_state_fields_default_values(self):
        """默认字段值正确"""
        state = AgentState(topic="测试选题")
        assert state.outline is None
        assert state.content is None
        assert state.adapted_content is None
        assert state.quality_score is None
        assert state.rewrite_reason is None
        assert state.rewrite_count == 0
        assert state.platform == "xiaohongshu"
        assert state.max_rewrites == 2

    def test_state_model_dump(self):
        """model_dump 正确序列化"""
        state = AgentState(
            topic="测试选题",
            outline="## 引言\n...",
            platform="douyin",
        )
        dump = state.model_dump()
        assert dump["topic"] == "测试选题"
        assert dump["outline"] == "## 引言\n..."
        assert dump["platform"] == "douyin"
        assert dump["rewrite_count"] == 0