"""
Embedder 模块测试
"""
import pytest
from apps.rag.embedder import TextChunker, Embedder, get_embedding_dimensions, LOCAL_EMBEDDING_DIM, EMBEDDING_DIMENSIONS


class TestTextChunker:
    """TextChunker 测试"""

    def test_chunk_text_basic(self):
        """基本分块测试"""
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "A" * 100
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 3  # 100/40 = 2.5 -> 3 chunks

    def test_chunk_text_empty(self):
        """空文本测试"""
        chunker = TextChunker()
        assert chunker.chunk_text("") == []
        assert chunker.chunk_text("   ") == []

    def test_chunk_text_short(self):
        """短文本测试"""
        chunker = TextChunker(chunk_size=100, overlap=20)
        text = "短文本内容"
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_with_overlap(self):
        """重叠分块测试"""
        chunker = TextChunker(chunk_size=10, overlap=5)
        text = "ABCDEFGHIJ"
        chunks = chunker.chunk_text(text)
        # ABCDEFGHIJ -> [ABCDEFGHIJ], start=5 -> [FGHIJ], done
        assert len(chunks) == 2
        # 第二个块应该包含重叠部分
        assert chunks[1] == "FGHIJ"


class TestEmbedder:
    """Embedder 测试"""

    def test_embedder_init(self):
        """Embedder 初始化测试"""
        embedder = Embedder()
        assert embedder.chunker is not None
        assert embedder.dimensions in (LOCAL_EMBEDDING_DIM, EMBEDDING_DIMENSIONS)

    def test_get_embedding_dimensions(self):
        """维度配置测试"""
        dim = get_embedding_dimensions()
        assert dim in (LOCAL_EMBEDDING_DIM, EMBEDDING_DIMENSIONS)


class TestLocalEmbedder:
    """Local Embedder 测试（需要真实模型）"""

    def test_local_embed_dimensions(self):
        """本地模型维度验证"""
        from apps.rag.embedder import LocalEmbedder
        embedder = LocalEmbedder()
        assert embedder.dimensions == LOCAL_EMBEDDING_DIM

    def test_local_embed_texts(self):
        """本地模型 embed 测试"""
        from apps.rag.embedder import LocalEmbedder
        embedder = LocalEmbedder()
        result = embedder.embed_texts(["hello world", "test"])
        assert len(result) == 2
        assert len(result[0]) == LOCAL_EMBEDDING_DIM

    def test_local_embed_query(self):
        """本地模型 query 测试"""
        from apps.rag.embedder import LocalEmbedder
        embedder = LocalEmbedder()
        result = embedder.embed_query("hello")
        assert len(result) == LOCAL_EMBEDDING_DIM