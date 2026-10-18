"""创建异步业务库会话并校验 Alembic 迁移版本。"""

import os
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


Database_URL = os.environ.get("DATABASE_URL")
if not Database_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Put it in backend/.env or your shell environment."
    )

engine = create_async_engine(Database_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Login(DeclarativeBase):
    """作为普通业务模型的 SQLAlchemy 声明式基类。"""

    pass


NORMAL_ALEMBIC_VERSION_TABLE = "alembic_version"
NORMAL_ALEMBIC_UPGRADE_COMMAND = "alembic -c normal_system/alembic.ini upgrade head"
NORMAL_ALEMBIC_STAMP_COMMAND = "alembic -c normal_system/alembic.ini stamp head"


def get_normal_alembic_head_revision() -> str:
    """读取迁移脚本的唯一 head，存在多个 head 时抛出 RuntimeError。"""
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "normal_system" / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(backend_root / "normal_system" / "alembic"),
    )
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected exactly one normal Alembic head, found: {heads}")
    return heads[0]


def build_missing_normal_migration_error() -> str:
    """生成业务库版本表缺失或不可读时的操作提示。"""
    return (
        f"Normal database migrations are not applied. Missing or unreadable "
        f"{NORMAL_ALEMBIC_VERSION_TABLE}. For an empty normal database run: "
        f"{NORMAL_ALEMBIC_UPGRADE_COMMAND}. If the legacy normal tables already "
        f"exist and match the current schema, run: {NORMAL_ALEMBIC_STAMP_COMMAND}"
    )


def build_normal_migration_revision_mismatch_error(
    current_revision: str | None,
    head_revision: str,
) -> str:
    """根据当前版本与目标版本生成迁移提示。"""
    current = current_revision or "<none>"
    return (
        "Normal database migrations are not at head. "
        f"Current revision: {current}. Expected head: {head_revision}. Run: "
        f"{NORMAL_ALEMBIC_UPGRADE_COMMAND}"
    )


def assert_normal_migration_revision_is_head(
    current_revision: str | None,
    head_revision: str,
) -> None:
    """确认数据库版本等于脚本 head，不一致时抛出 RuntimeError。"""
    if current_revision != head_revision:
        raise RuntimeError(
            build_normal_migration_revision_mismatch_error(
                current_revision,
                head_revision,
            )
        )


async def verify_normal_migrations_applied() -> None:
    """读取业务库迁移版本，未应用或未到 head 时抛出 RuntimeError。"""
    head_revision = get_normal_alembic_head_revision()
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text(f"SELECT version_num FROM {NORMAL_ALEMBIC_VERSION_TABLE} LIMIT 1")
            )
            current_revision = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        raise RuntimeError(build_missing_normal_migration_error()) from exc
    assert_normal_migration_revision_is_head(current_revision, head_revision)


async def get_db():
    """为一次 HTTP 请求提供独立数据库会话。

    Yields:
        请求使用的异步会话；业务服务负责提交，依赖退出时关闭会话。
    """
    async with async_session() as session:
        yield session
