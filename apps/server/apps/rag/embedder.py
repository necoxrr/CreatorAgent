"""
RAG Embedding 模块
使用 OpenAI text-embedding-3-small 进行文本向量化
"""
import logging
from typing import AsyncGenerator
from openai import AsyncOpenAI
from ..config import get_settings

logger = logging.getLogger(__name__)

# Embedding 模型配置
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# 分块配置
CHUNK_SIZE = 500  # 字符数
CHUNK_OVERLAP = 50  # 重叠字符数


class TextChunker:
    """文本分块器"""

    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """将文本分割成重叠的块"""
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap
            if start >= len(text):
                break

        return chunks


class Embedder:
    """OpenAI Embedding 封装"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.chunker = TextChunker()

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        将多个文本转换为向量

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        try:
            response = await self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    async def embed_chunked_text(self, text: str) -> tuple[list[str], list[list[float]]]:
        """
        将文本分块并向量化

        Args:
            text: 原始文本

        Returns:
            (文本块列表, 向量列表)
        """
        chunks = self.chunker.chunk_text(text)
        if not chunks:
            return [], []

        vectors = await self.embed_texts(chunks)
        return chunks, vectors

    async def embed_query(self, query: str) -> list[float]:
        """
        将查询文本向量化

        Args:
            query: 查询文本

        Returns:
            查询向量
        """
        vectors = await self.embed_texts([query])
        return vectors[0]


def get_embedder() -> Embedder:
    """获取 Embedder 实例（线程安全）"""
    return Embedder()