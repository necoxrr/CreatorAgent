"""
Embedder 模块测试
"""
import pytest
from apps.rag.embedder import TextChunker, Embedder


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
    """Embedder 测试（需要 mock OpenAI）"""

    def test_embedder_init(self):
        """Embedder 初始化测试"""
        embedder = Embedder()
        assert embedder.client is not None
        assert embedder.chunker is not None