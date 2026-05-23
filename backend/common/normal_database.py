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
    raise RuntimeError("DATABASE_URL is not set. Put it in backend/.env or your shell environment.")

engine = create_async_engine(Database_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Login(DeclarativeBase):
    pass


NORMAL_ALEMBIC_VERSION_TABLE = "alembic_version"
NORMAL_ALEMBIC_UPGRADE_COMMAND = "alembic -c normal_system/alembic.ini upgrade head"
NORMAL_ALEMBIC_STAMP_COMMAND = "alembic -c normal_system/alembic.ini stamp head"


def get_normal_alembic_head_revision() -> str:
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
    if current_revision != head_revision:
        raise RuntimeError(
            build_normal_migration_revision_mismatch_error(
                current_revision,
                head_revision,
            )
        )


async def verify_normal_migrations_applied() -> None:
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
    async with async_session() as session:
        yield session
