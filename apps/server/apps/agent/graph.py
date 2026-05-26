"""
Graph 入口 — 组装所有节点，暴露 runnable
"""
import logging
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    outline_generator,
    content_writer,
    style_adapter,
    quality_checker,
    rewrite_agent,
)

logger = logging.getLogger(__name__)

# 节点名称常量
NODE_OUTLINE = "outline_generator"
NODE_CONTENT = "content_writer"
NODE_ADAPTER = "style_adapter"
NODE_QUALITY = "quality_checker"
NODE_REWRITE = "rewrite_agent"


def _route_quality(state: AgentState) -> str:
    """条件分支路由：根据质检结果决定下一步"""
    if state.should_rewrite():
        logger.info(f"[路由] quality={state.quality_score} < 7，重写流程，rewrite_count={state.rewrite_count}")
        return NODE_REWRITE
    logger.info(f"[路由] quality={state.quality_score} >= 7 或已达重写上限，结束流程")
    return END


def create_agent_graph() -> StateGraph:
    """构建 Agent StateGraph"""
    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node(NODE_OUTLINE, outline_generator.generate)
    graph.add_node(NODE_CONTENT, content_writer.generate)
    graph.add_node(NODE_ADAPTER, style_adapter.adapt)
    graph.add_node(NODE_QUALITY, quality_checker.check)
    graph.add_node(NODE_REWRITE, rewrite_agent.rewrite)

    # 设置入口
    graph.set_entry_point(NODE_OUTLINE)

    # 主流程：outline → content → adapter → quality
    graph.add_edge(NODE_OUTLINE, NODE_CONTENT)
    graph.add_edge(NODE_CONTENT, NODE_ADAPTER)
    graph.add_edge(NODE_ADAPTER, NODE_QUALITY)

    # 条件分支：quality → rewrite 或 END
    graph.add_conditional_edges(
        NODE_QUALITY,
        _route_quality,
        {
            NODE_REWRITE: NODE_REWRITE,
            END: END,
        },
    )

    # rewrite 后回到 adapter 重新适配
    graph.add_edge(NODE_REWRITE, NODE_ADAPTER)

    return graph


# 单例 runnable（延迟构建）
_agent_runnable = None


def get_agent_runnable():
    """获取全局单例 Agent runnable"""
    global _agent_runnable
    if _agent_runnable is None:
        _agent_runnable = create_agent_graph().compile()
    return _agent_runnable