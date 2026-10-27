"""管理业务库启动校验和连接池释放。"""

from contextlib import asynccontextmanager

from common.auth import get_access_token_expire_seconds, get_jwt_secret
from common.gate_cookie import get_gate_cookie_secret
from common.normal_database import engine
from fastapi import FastAPI
from normal_system.bootstrap import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """管理配置、迁移启动校验和退出时的连接池清理。

    Args:
        _app: FastAPI 传入的应用实例，生命周期处理不读取其实例状态。

    Yields:
        完成数据库迁移校验后，将控制权交还应用运行阶段。

    Raises:
        RuntimeError: 签名密钥或令牌有效期配置非法，或业务库迁移未达到当前 head。
    """
    try:
        jwt_secret = get_jwt_secret()
        gate_secret = get_gate_cookie_secret()
        if jwt_secret == gate_secret:
            raise RuntimeError("CHAT_GATE_COOKIE_SECRET 必须与 CHAT_JWT_SECRET 不同")
        get_access_token_expire_seconds()
        await init_db()
        yield
    finally:
        await engine.dispose()
