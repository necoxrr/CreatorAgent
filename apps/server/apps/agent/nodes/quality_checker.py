"""
节点4：质检评分 + 修改意见（异步版本）
"""
import logging
import re
from ..state import AgentState

logger = logging.getLogger(__name__)

PROMPT_QUALITY = """你是一个资深内容质量审核员。请对以下内容进行质检并打分。

内容：
{content}

平台：{platform}

评分维度（每项 0-10）：
1. 内容价值：信息增量、有用性、独特视角
2. 语言表达：流畅度、专业性、感染力
3. 平台适配：语言风格、格式规范、标签使用
4. 结构逻辑：开头、结尾、层次分明
5. 合规安全：无敏感词、无误导性内容

请输出以下格式的评分结果（严格按此格式）：
SCORE: [总分 0-10]
REASON: [修改意见，100字以内，描述主要问题和不足]
"""

RE_SCORE = re.compile(r"SCORE:\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
RE_REASON = re.compile(r"REASON:\s*(.+)", re.IGNORECASE | re.DOTALL)


async def check(state: AgentState) -> AgentState:
    """接收 adapted_content，输出 quality_score + rewrite_reason（异步）"""
    if not state.adapted_content:
        raise ValueError("[quality_checker] adapted_content 为空，无法质检")

    logger.info(f"[quality_checker] 开始质检，长度={len(state.adapted_content)}")

    from ..llm import get_llm_client
    client = get_llm_client()

    prompt = PROMPT_QUALITY.format(
        content=state.adapted_content,
        platform=state.platform,
    )
    response = await client.generate_async(prompt)
    logger.info(f"[quality_checker] 质检完成，raw_response={response[:200]}")

    score_match = RE_SCORE.search(response)
    score = float(score_match.group(1)) if score_match else 0.0

    reason_match = RE_REASON.search(response)
    reason = reason_match.group(1).strip() if reason_match else "内容存在质量问题"

    score = max(0.0, min(10.0, score))

    logger.info(f"[quality_checker] 评分={score}，reason={reason}")
    new_state = state.model_dump()
    new_state["quality_score"] = float(score)
    new_state["rewrite_reason"] = str(reason)
    return AgentState(**new_state)