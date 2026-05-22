"""
ChromaDB 向量存储模块
支持 collection 初始化、批量写入和语义检索
"""
import logging
from typing import Optional
from chromadb import PersistentClient, Settings
from .embedder import get_embedding_dimensions

logger = logging.getLogger(__name__)

# Collection 配置
COLLECTION_NAME = "topics"
TOP_K = 10


class VectorStore:
    """ChromaDB 向量存储封装"""

    def __init__(self, persist_directory: str = "./chroma_data"):
        self.persist_directory = persist_directory
        self._client: Optional[PersistentClient] = None
        self._collection = None
        self._dimension = get_embedding_dimensions()

    def initialize(self, force_recreate: bool = False) -> None:
        """
        初始化 ChromaDB 客户端和 collection

        Args:
            force_recreate: 若为 True，删除旧 collection 并重建（embedding dimension 变更时需要）
        """
        try:
            self._client = PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )

            if force_recreate:
                try:
                    self._client.delete_collection(name=COLLECTION_NAME)
                    logger.info(f"Deleted old collection: {COLLECTION_NAME}")
                except Exception:
                    pass

            # 获取或创建 collection
            try:
                self._collection = self._client.get_collection(name=COLLECTION_NAME)
                logger.info(f"Connected to existing collection: {COLLECTION_NAME}")
            except Exception:
                self._collection = self._client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={
                        "description": "Topics for RAG retrieval",
                        "embedding_dimension": self._dimension,
                    },
                )
                logger.info(f"Created new collection: {COLLECTION_NAME}, dim={self._dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_documents(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """
        批量添加文档到 collection

        Args:
            ids: 文档 ID 列表
            embeddings: 向量列表
            documents: 文档内容列表
            metadatas: 元数据列表
        """
        if not self._collection:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")

        if not all(len(lst) == len(ids) for lst in [embeddings, documents]):
            raise ValueError("IDs, embeddings, and documents must have the same length")

        try:
            # 只在有实际 metadata 时传递，否则传 None（ChromaDB 新版要求）
            has_metadata = metadatas and any(bool(m) for m in metadatas)
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas if has_metadata else None,
            )
            logger.info(f"Added {len(ids)} documents to collection")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def similarity_search(
        self,
        query_embedding: list[float],
        n_results: int = TOP_K,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """
        语义检索

        Args:
            query_embedding: 查询向量
            n_results: 返回数量
            where: 元数据过滤条件

        Returns:
            检索结果列表
        """
        if not self._collection:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
            )

            # 格式化结果
            formatted_results = []
            if results and results.get("ids"):
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    })

            return formatted_results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise

    def delete_collection(self) -> None:
        """删除 collection"""
        if not self._client:
            raise RuntimeError("Client not initialized")

        try:
            self._client.delete_collection(name=COLLECTION_NAME)
            logger.info(f"Deleted collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    def close(self) -> None:
        """关闭客户端"""
        self._client = None
        self._collection = None

    @property
    def embedding_dimension(self) -> int:
        """获取当前 embedding 维度"""
        return self._dimension


# 全局单例
_vector_store: Optional[VectorStore] = None


def get_vector_store(
    persist_directory: str = "./chroma_data",
    force_recreate: bool = False,
) -> VectorStore:
    """
    获取 VectorStore 单例

    Args:
        persist_directory: ChromaDB 数据目录
        force_recreate: 是否强制重建 collection（embedding dimension 变更时传 True）
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_directory)
        _vector_store.initialize(force_recreate=force_recreate)
    return _vector_store


def close_vector_store() -> None:
    """关闭 VectorStore"""
    global _vector_store
    if _vector_store:
        _vector_store.close()
        _vector_store = None


def reset_vector_store(persist_directory: str = "./chroma_data") -> VectorStore:
    """重置 VectorStore（用于 embedding dimension 变更后重建）"""
    global _vector_store
    if _vector_store:
        _vector_store.close()
    _vector_store = VectorStore(persist_directory)
    _vector_store.initialize(force_recreate=True)
    return _vector_store