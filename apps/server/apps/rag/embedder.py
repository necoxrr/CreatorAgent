"""
RAG Embedding 模块
支持 local（sentence-transformers）和 openai 两种 provider
"""
import logging
from functools import lru_cache
from typing import Optional
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from ..config import get_settings

logger = logging.getLogger(__name__)

# Embedding 模型配置
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"
LOCAL_EMBEDDING_DIM = 384

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


class BaseEmbedder:
    """Embedding 接口基类"""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量"""
        raise NotImplementedError

    def embed_query(self, query: str) -> list[float]:
        """将查询文本向量化"""
        raise NotImplementedError


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI Embedding provider"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.dimensions = EMBEDDING_DIMENSIONS

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量（异步）"""
        if not texts:
            return []

        try:
            response = await self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
                dimensions=self.dimensions,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise

    def embed_query(self, query: str) -> list[float]:
        """将查询文本向量化（同步包装）"""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.embed_texts([query])
        )[0]


class LocalEmbedder(BaseEmbedder):
    """本地 sentence-transformers Embedding provider（单例）"""

    _instance: Optional["LocalEmbedder"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LocalEmbedder._model is None:
            logger.info(f"Loading local embedding model: {LOCAL_MODEL_NAME}")
            import os
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            LocalEmbedder._model = SentenceTransformer(
                LOCAL_MODEL_NAME,
                device="cpu",
                cache_folder=os.path.expanduser("~/.cache/huggingface/hub"),
            )
            logger.info(f"Model loaded, dimension: {LOCAL_EMBEDDING_DIM}")

    @property
    def dimensions(self) -> int:
        return LOCAL_EMBEDDING_DIM

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量（同步）"""
        if not texts:
            return []

        try:
            embeddings = LocalEmbedder._model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            raise

    def embed_query(self, query: str) -> list[float]:
        """将查询文本向量化（同步）"""
        return self.embed_texts([query])[0]


class Embedder:
    """Embedding 工厂类，根据配置选择 provider"""

    def __init__(self):
        settings = get_settings()
        provider = settings.EMBEDDING_PROVIDER

        if provider == "openai":
            self._impl = OpenAIEmbedder()
            self._dimensions = EMBEDDING_DIMENSIONS
        else:
            self._impl = LocalEmbedder()
            self._dimensions = LOCAL_EMBEDDING_DIM

        self.chunker = TextChunker()
        logger.info(f"Embedder initialized with provider: {provider}, dim: {self._dimensions}")

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量"""
        return self._impl.embed_texts(texts)

    async def embed_texts_async(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量（异步接口）"""
        if isinstance(self._impl, OpenAIEmbedder):
            return await self._impl.embed_texts(texts)
        return self._impl.embed_texts(texts)

    def embed_query(self, query: str) -> list[float]:
        """将查询文本向量化"""
        return self._impl.embed_query(query)

    def embed_chunked_text(self, text: str) -> tuple[list[str], list[list[float]]]:
        """将文本分块并向量化"""
        chunks = self.chunker.chunk_text(text)
        if not chunks:
            return [], []

        vectors = self.embed_texts(chunks)
        return chunks, vectors


@lru_cache
def get_embedder() -> Embedder:
    """获取 Embedder 单例（线程安全）"""
    return Embedder()


def get_embedding_dimensions() -> int:
    """获取当前 provider 的向量维度"""
    settings = get_settings()
    if settings.EMBEDDING_PROVIDER == "openai":
        return EMBEDDING_DIMENSIONS
    return LOCAL_EMBEDDING_DIM