"""
pytest 配置
"""
import os
import sys
from pathlib import Path

# 将 apps/server 加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试环境变量
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("FIRECRAWL_API_KEY", "test-firecrawl-key")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("DEBUG", "true")