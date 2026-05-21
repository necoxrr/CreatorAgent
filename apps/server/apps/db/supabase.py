"""
Supabase 数据库客户端
"""
from supabase import create_client, Client
from ..config import get_settings

# 延迟初始化，避免模块导入时 URL 还没加载
_supabase_client: Client | None = None


def get_supabase() -> Client:
    """获取 Supabase 客户端"""
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )
    return _supabase_client
