"""在应用启动时校验普通业务库迁移。"""

from common.normal_database import verify_normal_migrations_applied


async def init_db() -> None:
    """加载业务模型并校验普通业务库已应用当前迁移。"""
    import normal_system.models  # noqa: F401

    await verify_normal_migrations_applied()
