"""
抖音热搜 API 客户端
使用抖音公开接口，无需认证
"""
import logging
import requests
from typing import TypedDict

logger = logging.getLogger(__name__)


class TrendingItem(TypedDict):
    """热搜条目"""
    title: str
    platform: str
    heat_score: int
    url: str | None


class DouyinClient:
    """抖音热搜 API 客户端"""

    def __init__(self):
        self.base_url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"

    def crawl_platform(self, platform: str = "douyin") -> list[TrendingItem]:
        """
        获取抖音热搜列表

        Args:
            platform: 平台名称 (仅支持 'douyin')

        Returns:
            热搜条目列表
        """
        if platform != "douyin":
            raise ValueError(f"不支持的平台: {platform}")

        try:
            response = requests.get(
                self.base_url,
                params={
                    "device_platform": "webapp",
                    "aid": "6383",
                    "channel": "pc_client",
                    "update_version": "1",
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://www.douyin.com/",
                    "Accept": "application/json",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            items: list[TrendingItem] = []
            word_list = data.get("data", {}).get("word_list", [])

            for entry in word_list:
                items.append({
                    "title": entry.get("word", ""),
                    "platform": "douyin",
                    "heat_score": entry.get("hot_value", 0),
                    "url": None,
                })

            logger.info(f"抖音热搜获取成功，共 {len(items)} 条")
            return items

        except Exception as e:
            logger.error(f"抖音热搜获取失败: {e}")
            raise