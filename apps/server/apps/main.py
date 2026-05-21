"""
CreatorAgent FastAPI 服务入口
端口: 8000
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api.v1 import trends
from .crawler.scheduler import start_scheduler, setup_scheduler

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("CreatorAgent 服务启动中...")
    setup_scheduler()
    start_scheduler()
    logger.info("服务启动完成")
    yield
    # 关闭时
    logger.info("CreatorAgent 服务关闭中...")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()

    app = FastAPI(
        title="CreatorAgent API",
        description="面向小红书/抖音创作者的 AI 智能体平台后端",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(trends.router)

    @app.get("/health")
    async def health_check() -> dict:
        """健康检查"""
        return {"status": "ok", "service": "creator-agent-server"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    # 直接传递 app 实例，避免字符串导入
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
