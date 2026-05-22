"""
手动重建 ChromaDB 索引脚本
把 Supabase hot_topics 表里的已有数据批量写入 ChromaDB
"""
import asyncio
import argparse
from apps.db.supabase import get_supabase
from apps.rag.vector_store import reset_vector_store
from apps.rag.embedder import get_embedder


async def reindex_all(batch_size: int = 50):
    """从 Supabase 批量重建索引"""
    supabase = get_supabase()
    embedder = get_embedder()

    # 重置 VectorStore（删除旧 collection 再重建，维度匹配 local 384）
    vector_store = reset_vector_store()

    print(f"开始重建索引，batch_size={batch_size}")

    offset = 0
    total = 0

    while True:
        result = supabase.table("hot_topics").select("*").limit(batch_size).offset(offset).execute()
        if not result.data:
            break

        ids = []
        texts = []
        metadatas = []

        for topic in result.data:
            topic_id = topic.get("id") or str(hash(topic.get("title", "")))
            title = topic.get("title", "")
            content = f"{title} {topic.get('url') or ''}"
            ids.append(topic_id)
            texts.append(content)
            metadatas.append({
                "platform": topic.get("platform", ""),
                "heat_score": topic.get("heat_score") or 0,
            })

        vectors = embedder.embed_texts(texts)

        vector_store.add_documents(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas,
        )

        total += len(ids)
        print(f"已索引 {total} 条")
        offset += batch_size

        if len(result.data) < batch_size:
            break

    print(f"索引重建完成，共 {total} 条")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="重建 ChromaDB 索引")
    parser.add_argument("--batch-size", type=int, default=50, help="批量大小")
    args = parser.parse_args()

    asyncio.run(reindex_all(args.batch_size))