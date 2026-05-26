"""
节点1：选题 → 结构化大纲（异步版本）
"""
import logging
from ..state import AgentState

logger = logging.getLogger(__name__)

PROMPT_OUTLINE = """你是一个资深内容策划。请根据以下选题，生成一份结构化大纲。

选题：{topic}
平台：{platform}

要求：
1. 大纲采用 Markdown 格式
2. 包含引言、正文（3-5个要点）、结语三部分
3. 每个正文要点需包含：小标题 + 一句话核心观点 + 展开思路（2-3句）

请直接输出大纲，不需要额外解释。"""


async def generate(state: AgentState) -> AgentState:
    """接收 topic，生成 outline（异步）"""
    logger.info(f"[outline_generator] 开始生成大纲，topic={state.topic}")

    from ..llm import get_llm_client
    client = get_llm_client()

    prompt = PROMPT_OUTLINE.format(topic=state.topic, platform=state.platform)
    response = await client.generate_async(prompt)

    logger.info(f"[outline_generator] 大纲生成完成，长度={len(response)}")
    new_state = state.model_dump()
    new_state["outline"] = response
    return AgentState(**new_state)