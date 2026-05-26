"""
LLM 客户端 — 支持 OpenAI / MiniMax / 本地模型
"""
import logging
import asyncio
import concurrent.futures
from functools import lru_cache
from typing import Optional
from openai import AsyncOpenAI
from ..config import get_settings

logger = logging.getLogger(__name__)

# 默认模型配置
DEFAULT_MODEL = "MiniMax-M2.7"


class LLMClient:
    """LLM 统一客户端（支持 OpenAI / MiniMax / Ollama）"""

    _instance: Optional["LLMClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        settings = get_settings()
        api_key = settings.OPENAI_API_KEY
        base_url = getattr(settings, "OPENAI_BASE_URL", None) or "https://api.minimax.chat"

        if api_key:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"LLMClient initialized with base_url={base_url}")
        else:
            logger.warning("OPENAI_API_KEY 未配置，LLM 将使用占位返回")
            self.client = None
        self._initialized = True

    def generate(self, prompt: str) -> str:
        """
        同步生成文本
        LangGraph 节点在同步上下文中调用此方法。
        通过在线程池执行来避免嵌套 asyncio.run() 问题。
        """
        if not self.client:
            return _placeholder_response(prompt)

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._sync_wrapper, prompt)
            return future.result(timeout=60)

    def _sync_wrapper(self, prompt: str) -> str:
        """在线程池的独立线程中创建新的事件循环来执行异步代码"""
        return asyncio.run(self._generate_impl(prompt))

    async def generate_async(self, prompt: str) -> str:
        """异步生成（需在 async 上下文中调用）"""
        if not self.client:
            return _placeholder_response(prompt)
        return await self._generate_impl(prompt)

    async def _generate_impl(self, prompt: str) -> str:
        """生成实现（异步）"""
        if not self.client:
            return _placeholder_response(prompt)

        try:
            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM generate failed: {e}")
            return _placeholder_response(prompt)


def _placeholder_response(prompt: str) -> str:
    """当无 LLM 时返回占位内容（方便开发调试）"""
    length = min(len(prompt), 100)
    preview = prompt[:length]
    return f"[Placeholder] 请求已接收，长度 {length}，请配置 OPENAI_API_KEY 以启用真实 LLM。预览: {preview}"


@lru_cache
def get_llm_client() -> LLMClient:
    """获取 LLM 客户端单例"""
    return LLMClient()