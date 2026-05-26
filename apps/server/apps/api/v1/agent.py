"""
Agent API 路由
POST /api/v1/agent/generate — Agent 生成流水线
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...db.supabase import get_supabase
from ...agent.graph import get_agent_runnable
from ...agent.state import AgentState

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])


class GenerateRequest(BaseModel):
    """Agent 生成请求"""
    topic: str
    platform: str = "xiaohongshu"
    max_rewrites: int = 2


class GenerateResponse(BaseModel):
    """Agent 生成响应"""
    outline: str | None = None
    content: str | None = None
    adapted_content: str | None = None
    quality_score: float | None = None
    rewrite_count: int = 0


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """
    触发 Agent 流水线：选题 → 大纲 → 初稿 → 适配 → 质检 → 重写

    - quality >= 7 则流程结束
    - quality < 7 则最多重写 max_rewrites 次
    """
    try:
        logger.info(f"Agent 生成请求: topic={request.topic}, platform={request.platform}")

        runnable = get_agent_runnable()
        initial_state = AgentState(
            topic=request.topic,
            platform=request.platform,
            max_rewrites=request.max_rewrites,
        )

        final_state = await runnable.ainvoke(initial_state)

        logger.info(
            f"Agent 流程完成: quality={final_state.get('quality_score')}, "
            f"rewrite_count={final_state.get('rewrite_count')}"
        )

        return GenerateResponse(
            outline=final_state.get("outline"),
            content=final_state.get("content"),
            adapted_content=final_state.get("adapted_content"),
            quality_score=final_state.get("quality_score"),
            rewrite_count=final_state.get("rewrite_count", 0),
        )

    except Exception as e:
        logger.error(f"Agent 生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))