"""
定时任务调度器
每天 8:00、12:00、18:00 自动抓取热搜
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .firecrawl_client import FirecrawlClient, TrendingItem
from .douyin_client import DouyinClient
from ..db.supabase import get_supabase

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def crawl_and_save(platform: str) -> int:
    """
    抓取指定平台热搜并保存到数据库

    Args:
        platform: 平台名称 ('xiaohongshu' | 'douyin')

    Returns:
        保存的条目数量
    """
    items: list[TrendingItem] = []

    if platform == "douyin":
        # 抖音使用免费 API
        client = DouyinClient()
        items = client.crawl_platform(platform)
    elif platform == "xiaohongshu":
        # 小红书使用 Firecrawl（需要 API key）
        from ..config import get_settings
        settings = get_settings()
        if not settings.FIRECRAWL_API_KEY:
            logger.warning("FIRECRAWL_API_KEY 未设置，跳过小红书抓取")
            return 0
        try:
            client = FirecrawlClient()
            items = client.crawl_platform(platform)
        except Exception as e:
            logger.warning(f"小红书抓取失败，跳过: {e}")
            return 0
    else:
        raise ValueError(f"不支持的平台: {platform}")

    if not items:
        logger.warning(f"[{platform}] 未抓到任何热搜")
        return 0

    supabase = get_supabase()
    # 批量插入
    result = supabase.table("hot_topics").insert(items).execute()
    logger.info(f"[{platform}] 保存 {len(result.data)} 条热搜到数据库")

    # 写入 ChromaDB 向量索引
    try:
        await index_topics_to_chroma(result.data)
    except Exception as e:
        logger.warning(f"[{platform}] ChromaDB 索引失败: {e}")

    return len(result.data)


async def index_topics_to_chroma(topics: list[dict]) -> None:
    """
    将 topics 批量写入 ChromaDB

    Args:
        topics: 从 Supabase 返回的 hot_topics 记录列表
    """
    if not topics:
        return

    from ..rag.embedder import get_embedder
    from ..rag.vector_store import get_vector_store

    embedder = get_embedder()
    vector_store = get_vector_store()

    # 准备嵌入数据
    ids = []
    texts = []
    metadatas = []

    for topic in topics:
        topic_id = topic.get("id") or str(hash(topic.get("title", "")))
        title = topic.get("title", "")
        content = f"{title} {topic.get('url') or ''}"
        ids.append(topic_id)
        texts.append(content)
        metadatas.append({
            "platform": topic.get("platform", ""),
            "heat_score": topic.get("heat_score") or 0,
        })

    # 批量向量化（local provider 是同步的，直接调用）
    vectors = embedder.embed_texts(texts)

    # 写入 ChromaDB
    vector_store.add_documents(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )
    logger.info(f"已索引 {len(ids)} 条到 ChromaDB")


async def crawl_trending() -> None:
    """定时抓取任务"""
    logger.info("开始执行定时抓取任务...")

    platforms = ["xiaohongshu", "douyin"]
    total = 0

    for platform in platforms:
        try:
            count = await crawl_and_save(platform)
            total += count
        except Exception as e:
            logger.error(f"[{platform}] 抓取失败: {e}")

    logger.info(f"定时抓取完成，共处理 {total} 条热搜")


def setup_scheduler() -> None:
    """注册定时任务"""
    # 早间 8:00
    scheduler.add_job(
        crawl_trending,
        CronTrigger(hour=8, minute=0),
        id="crawl_8am",
        name="早间热搜抓取",
        replace_existing=True,
    )
    logger.info("注册定时任务: 早间热搜抓取 (08:00)")

    # 午间 12:00
    scheduler.add_job(
        crawl_trending,
        CronTrigger(hour=12, minute=0),
        id="crawl_12pm",
        name="午间热搜抓取",
        replace_existing=True,
    )
    logger.info("注册定时任务: 午间热搜抓取 (12:00)")

    # 晚间 18:00
    scheduler.add_job(
        crawl_trending,
        CronTrigger(hour=18, minute=0),
        id="crawl_6pm",
        name="晚间热搜抓取",
        replace_existing=True,
    )
    logger.info("注册定时任务: 晚间热搜抓取 (18:00)")


def start_scheduler() -> None:
    """启动调度器"""
    setup_scheduler()
    scheduler.start()
    logger.info("定时任务调度器已启动")
