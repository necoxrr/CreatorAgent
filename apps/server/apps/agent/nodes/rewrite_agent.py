"""
节点5：根据质检意见重写（异步版本）
"""
import logging
from ..state import AgentState

logger = logging.getLogger(__name__)

PROMPT_REWRITE = """你是一个资深内容编辑。请根据以下修改意见，对内容进行重写。

原始内容：
{content}

修改意见：
{reason}

平台：{platform}

要求：
1. 严格按照修改意见进行重写
2. 保留平台适配特性
3. 不要完全重写，而是在原基础上修改不足之处
4. 字数可适当调整

请直接输出重写后内容，不需要额外解释。"""


async def rewrite(state: AgentState) -> AgentState:
    """接收 content + rewrite_reason，输出重写后的 content（异步）"""
    if not state.content:
        raise ValueError("[rewrite_agent] content 为空，无法重写")
    if not state.rewrite_reason:
        raise ValueError("[rewrite_agent] rewrite_reason 为空，无法重写")

    new_count = state.rewrite_count + 1
    logger.info(f"[rewrite_agent] 开始第 {new_count} 次重写，reason={state.rewrite_reason}")

    from ..llm import get_llm_client
    client = get_llm_client()

    prompt = PROMPT_REWRITE.format(
        content=state.content,
        reason=state.rewrite_reason,
        platform=state.platform,
    )
    response = await client.generate_async(prompt)

    logger.info(f"[rewrite_agent] 重写完成，长度={len(response)}")
    new_state = state.model_dump()
    new_state["content"] = response
    new_state["rewrite_count"] = new_count
    return AgentState(**new_state)