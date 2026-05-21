"""
热点话题 API 测试
覆盖：GET /api/v1/trends（正常/空数据/平台过滤）+ POST /api/v1/trends/refresh
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_supabase():
    """Mock Supabase 客户端"""
    mock = MagicMock()
    return mock


@pytest.fixture
def client():
    """创建测试客户端"""
    from apps.main import app
    return TestClient(app)


class TestGetTrends:
    """GET /api/v1/trends/ 测试"""

    @patch("apps.api.v1.trends.get_supabase")
    def test_get_trends_success(self, mock_get_supabase, client):
        """正常返回热点列表"""
        mock_data = [
            {
                "id": "1",
                "title": "测试热搜1",
                "url": "https://xiaohongshu.com/explore/1",
                "platform": "xiaohongshu",
                "heat_score": 10000,
                "crawled_at": "2026-05-21T08:00:00Z",
            },
            {
                "id": "2",
                "title": "测试热搜2",
                "url": "https://douyin.com/hot/2",
                "platform": "douyin",
                "heat_score": 8000,
                "crawled_at": "2026-05-21T08:00:00Z",
            },
        ]
        mock_table = MagicMock()
        mock_table.select.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=mock_data)

        mock_supabase = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/api/v1/trends/")

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert len(response.json()["data"]) == 2
        assert response.json()["data"][0]["title"] == "测试热搜1"

    @patch("apps.api.v1.trends.get_supabase")
    def test_get_trends_empty(self, mock_get_supabase, client):
        """空数据返回空列表"""
        mock_table = MagicMock()
        mock_table.select.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[])

        mock_supabase = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/api/v1/trends/")

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"] == []

    @patch("apps.api.v1.trends.get_supabase")
    def test_get_trends_filter_platform(self, mock_get_supabase, client):
        """平台过滤"""
        mock_table = MagicMock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[
            {
                "id": "1",
                "title": "小红书热搜",
                "platform": "xiaohongshu",
                "heat_score": 5000,
                "crawled_at": "2026-05-21T08:00:00Z",
            }
        ])

        mock_supabase = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/api/v1/trends/?platform=xiaohongshu")

        assert response.status_code == 200
        assert response.json()["code"] == 0
        mock_table.eq.assert_called_once_with("platform", "xiaohongshu")

    @patch("apps.api.v1.trends.get_supabase")
    def test_get_trends_db_error(self, mock_get_supabase, client):
        """数据库异常返回 500"""
        mock_get_supabase.side_effect = Exception("DB connection failed")

        response = client.get("/api/v1/trends/")

        assert response.status_code == 500

    @patch("apps.api.v1.trends.get_supabase")
    def test_get_trends_limit_param(self, mock_get_supabase, client):
        """limit 参数校验"""
        mock_table = MagicMock()
        mock_table.select.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[])

        mock_supabase = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/api/v1/trends/?limit=50")

        assert response.status_code == 200
        mock_table.limit.assert_called_once_with(50)


class TestRefreshTrends:
    """POST /api/v1/trends/refresh 测试"""

    @patch("apps.crawler.scheduler.crawl_and_save", new_callable=AsyncMock, return_value=5)
    @patch("apps.crawler.firecrawl_client.FirecrawlClient")
    def test_refresh_success(self, mock_fc_client, mock_crawl_and_save, client):
        """手动触发抓取成功"""
        mock_fc_client.return_value = MagicMock()

        response = client.post("/api/v1/trends/refresh")

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert "抓取完成" in response.json()["message"]

    @patch("apps.crawler.scheduler.crawl_and_save", new_callable=AsyncMock, side_effect=Exception("抓取失败"))
    def test_refresh_internal_error(self, mock_crawl_and_save, client):
        """抓取过程异常"""
        response = client.post("/api/v1/trends/refresh")

        assert response.status_code == 200
        assert response.json()["code"] == 5001


class TestHealthCheck:
    """健康检查接口测试"""

    def test_health(self, client):
        """服务健康"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"