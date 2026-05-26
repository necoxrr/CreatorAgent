"""
节点2：大纲 → 全文初稿（异步版本）
"""
import logging
from ..state import AgentState

logger = logging.getLogger(__name__)

PROMPT_WRITER = """你是一个资深内容创作者。请根据以下大纲，撰写完整文章初稿。

选题：{topic}
平台：{platform}
大纲：
{outline}

要求：
1. 字数 800-1500 字
2. 语言风格适配 {platform} 平台调性
3. 标题吸引眼球，有爆点
4. 正文逻辑清晰，要点之间有承接
5. 结尾有行动号召（CTA）或互动引导

请直接输出正文，不需要额外解释。"""


async def generate(state: AgentState) -> AgentState:
    """接收 outline，生成 content（异步）"""
    if not state.outline:
        raise ValueError("[content_writer] outline 为空，无法生成初稿")

    logger.info(f"[content_writer] 开始生成初稿，outline长度={len(state.outline)}")

    from ..llm import get_llm_client
    client = get_llm_client()

    prompt = PROMPT_WRITER.format(
        topic=state.topic,
        platform=state.platform,
        outline=state.outline,
    )
    response = await client.generate_async(prompt)

    logger.info(f"[content_writer] 初稿生成完成，长度={len(response)}")
    new_state = state.model_dump()
    new_state["content"] = response
    return AgentState(**new_state)