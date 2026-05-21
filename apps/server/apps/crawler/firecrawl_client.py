"""
Firecrawl API 客户端
用于抓取小红书、抖音热搜页面
"""
import os
import logging
from typing import TypedDict
from bs4 import BeautifulSoup
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


class TrendingItem(TypedDict):
    """热搜条目"""
    title: str
    platform: str
    heat_score: int
    url: str | None


class FirecrawlClient:
    """Firecrawl API 客户端"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().FIRECRAWL_API_KEY
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY 环境变量未设置")
        self.base_url = "https://api.firecrawl.dev"
        self.client = httpx.Client(timeout=30.0)

    def scrape(self, url: str) -> dict:
        """
        调用 Firecrawl scrape 接口

        Args:
            url: 要抓取的页面 URL

        Returns:
            API 响应 JSON
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "url": url,
            "pageOptions": {"onlyMainContent": True},
        }
        response = self.client.post(
            f"{self.base_url}/v0/scrape",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def parse_xiaohongshu_trending(self, html: str) -> list[TrendingItem]:
        """
        解析小红书热搜页面

        Args:
            html: 页面 HTML 内容

        Returns:
            热搜条目列表
        """
        soup = BeautifulSoup(html, "lxml")
        items: list[TrendingItem] = []

        # 根据实际页面结构调整选择器
        for item in soup.select(".trending-item, .note-card, [data-vb-temp]"):
            title_elem = item.select_one(".title, .desc, .content")
            heat_elem = item.select_one(".heat, .likecount, .heat-index")

            if title_elem and title_elem.text.strip():
                title = title_elem.text.strip()
                heat_text = heat_elem.text if heat_elem else "0"
                # 尝试提取数字
                heat_score = self._parse_heat_score(heat_text)

                items.append({
                    "title": title,
                    "platform": "xiaohongshu",
                    "heat_score": heat_score,
                    "url": None,
                })

        logger.info(f"解析小红书热搜 {len(items)} 条")
        return items

    def parse_douyin_trending(self, html: str) -> list[TrendingItem]:
        """
        解析抖音热搜页面

        Args:
            html: 页面 HTML 内容

        Returns:
            热搜条目列表
        """
        soup = BeautifulSoup(html, "lxml")
        items: list[TrendingItem] = []

        for item in soup.select(".hot-item, .trend-item, [data-e2e]"):
            title_elem = item.select_one(".title, .hot-title, span")
            heat_elem = item.select_one(".hot-score, .heat, em")

            if title_elem and title_elem.text.strip():
                title = title_elem.text.strip()
                heat_text = heat_elem.text if heat_elem else "0"
                heat_score = self._parse_heat_score(heat_text)

                items.append({
                    "title": title,
                    "platform": "douyin",
                    "heat_score": heat_score,
                    "url": None,
                })

        logger.info(f"解析抖音热搜 {len(items)} 条")
        return items

    def _parse_heat_score(self, text: str) -> int:
        """从热度文本中提取数字"""
        import re
        # 提取所有数字
        numbers = re.findall(r'\d+', text)
        if not numbers:
            return 0
        # 返回第一个连续数字（可能是万、十万等单位）
        try:
            return int(numbers[0])
        except ValueError:
            return 0

    def crawl_platform(self, platform: str) -> list[TrendingItem]:
        """
        抓取指定平台的热搜

        Args:
            platform: 平台名称 ('xiaohongshu' | 'douyin')

        Returns:
            热搜条目列表
        """
        urls = {
            "xiaohongshu": "https://www.xiaohongshu.com/explore",
            "douyin": "https://www.douyin.com/hot",
        }

        if platform not in urls:
            raise ValueError(f"不支持的平台: {platform}")

        url = urls[platform]
        try:
            data = self.scrape(url)
            html = data.get("content", "")

            if platform == "xiaohongshu":
                return self.parse_xiaohongshu_trending(html)
            else:
                return self.parse_douyin_trending(html)
        except Exception as e:
            logger.error(f"抓取 {platform} 失败: {e}")
            raise
