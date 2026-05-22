"""
CreatorAgent 配置管理
所有配置从环境变量读取
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    """应用配置"""

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Firecrawl
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Embedding
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")  # "local" | "openai"

    # 服务
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    def validate(self) -> None:
        """验证必填配置"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL 环境变量未设置")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY 环境变量未设置")
        # FIRECRAWL_API_KEY 现在可选（小红书才需要）
        # if not self.FIRECRAWL_API_KEY:
        #     raise ValueError("FIRECRAWL_API_KEY 环境变量未设置")


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    settings.validate()
    return settings
