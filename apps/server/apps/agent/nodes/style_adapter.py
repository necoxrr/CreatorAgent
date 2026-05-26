"""
节点3：初稿 → 平台适配版本（异步版本）
"""
import logging
from ..state import AgentState

logger = logging.getLogger(__name__)

PROMPT_ADAPTER = """你是一个内容适配专家。请将以下初稿适配到 {platform} 平台。

原始初稿：
{content}

平台：{platform}

适配要求：
1. 调整语言风格和表达方式，契合平台用户习惯
2. 小红书：口语化、有情感共鸣、emoji 点缀、标签 (#话题)
3. 抖音：短句有力、节奏感强、适合口播
4. 保留核心信息和价值点
5. 适当调整篇幅（小红书800-1000字，抖音可更短）

请直接输出适配后内容，不需要额外解释。"""


async def adapt(state: AgentState) -> AgentState:
    """接收 content，输出平台适配版本（异步）"""
    if not state.content:
        raise ValueError("[style_adapter] content 为空，无法适配")

    logger.info(f"[style_adapter] 开始平台适配，platform={state.platform}")

    from ..llm import get_llm_client
    client = get_llm_client()

    prompt = PROMPT_ADAPTER.format(
        content=state.content,
        platform=state.platform,
    )
    response = await client.generate_async(prompt)

    logger.info(f"[style_adapter] 适配完成，长度={len(response)}")
    new_state = state.model_dump()
    new_state["adapted_content"] = response
    return AgentState(**new_state)