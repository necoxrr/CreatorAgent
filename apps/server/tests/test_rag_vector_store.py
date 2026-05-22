"""
VectorStore 模块测试
"""
import pytest
import tempfile
import shutil
from apps.rag.vector_store import VectorStore


class TestVectorStore:
    """VectorStore 测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        d = tempfile.mkdtemp()
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_initialize(self, temp_dir):
        """初始化测试"""
        store = VectorStore(persist_directory=temp_dir)
        store.initialize()
        assert store._client is not None
        assert store._collection is not None
        store.close()

    def test_add_documents(self, temp_dir):
        """添加文档测试"""
        store = VectorStore(persist_directory=temp_dir)
        store.initialize()

        ids = ["1", "2", "3"]
        embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
        documents = ["doc1", "doc2", "doc3"]

        store.add_documents(ids, embeddings, documents)
        store.close()

    def test_similarity_search(self, temp_dir):
        """语义检索测试"""
        store = VectorStore(persist_directory=temp_dir)
        store.initialize()

        ids = ["1", "2", "3"]
        embeddings = [[0.1] * 1536, [0.5] * 1536, [0.9] * 1536]
        documents = ["热门话题A", "普通话题B", "冷门话题C"]

        store.add_documents(ids, embeddings, documents)

        # 查询接近 id=1 的向量
        results = store.similarity_search([0.15] * 1536, n_results=2)
        assert len(results) == 2
        assert results[0]["id"] == "1"  # 最接近
        store.close()

    def test_empty_search(self, temp_dir):
        """空检索测试"""
        store = VectorStore(persist_directory=temp_dir)
        store.initialize()

        results = store.similarity_search([0.5] * 1536, n_results=5)
        assert results == []
        store.close()