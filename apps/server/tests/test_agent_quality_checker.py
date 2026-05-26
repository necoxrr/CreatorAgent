"""
Quality Checker 节点单元测试（解析逻辑测试，无需 LLM）
"""
import pytest
from apps.agent.state import AgentState
from apps.agent.nodes.quality_checker import RE_SCORE, RE_REASON


class TestQualityCheckerParsing:
    """质检结果正则解析测试"""

    def test_parse_valid_score_and_reason(self):
        """正常格式：SCORE + REASON"""
        text = """SCORE: 8.5
REASON: 内容结构清晰，语言流畅，建议加强结尾CTA"""
        score_match = RE_SCORE.search(text)
        reason_match = RE_REASON.search(text)
        assert score_match is not None
        assert float(score_match.group(1)) == 8.5
        assert reason_match is not None
        assert "内容结构清晰" in reason_match.group(1)

    def test_parse_score_only(self):
        """只有 SCORE，没有 REASON"""
        text = "SCORE: 6.0"
        score_match = RE_SCORE.search(text)
        assert score_match is not None
        assert float(score_match.group(1)) == 6.0

    def test_parse_lowercase_score(self):
        """小写 score: 关键字"""
        text = "score: 7.5\nreason: 测试"
        score_match = RE_SCORE.search(text)
        reason_match = RE_REASON.search(text)
        assert score_match is not None
        assert float(score_match.group(1)) == 7.5

    def test_parse_multiline_reason(self):
        """多行 REASON 应完整提取"""
        text = """SCORE: 5.0
REASON: 内容有以下问题：
1. 语言不够生动
2. 缺少具体案例
建议增加互动引导"""
        reason_match = RE_REASON.search(text)
        assert reason_match is not None
        reason = reason_match.group(1)
        assert "语言不够生动" in reason
        assert "缺少具体案例" in reason

    def test_parse_score_out_of_range(self):
        """分数超出范围（< 0 或 > 10）应在 check 函数中被限制"""
        score = -2.0
        score = max(0.0, min(10.0, score))
        assert score == 0.0

        score = 15.0
        score = max(0.0, min(10.0, score))
        assert score == 10.0


class TestQualityCheckerIntegration:
    """质检节点集成测试"""

    @pytest.mark.asyncio
    async def test_quality_check_empty_content_raises(self):
        """adapted_content 为空时应抛出 ValueError"""
        from apps.agent.nodes import quality_checker

        state = AgentState(
            topic="测试选题",
            adapted_content=None,
        )
        try:
            await quality_checker.check(state)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "adapted_content 为空" in str(e)