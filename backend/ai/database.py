import os
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class AIBase(DeclarativeBase):
    pass


_ai_engine: AsyncEngine | None = None
_ai_sessionmaker: async_sessionmaker[AsyncSession] | None = None
AI_ALEMBIC_VERSION_TABLE = "alembic_version"
AI_ALEMBIC_UPGRADE_COMMAND = "alembic -c ai/alembic.ini upgrade head"
AI_ALEMBIC_STAMP_COMMAND = "alembic -c ai/alembic.ini stamp head"


def get_ai_database_url() -> str:
    database_url = os.environ.get("AI_DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "AI_DATABASE_URL is not set. Put it in backend/.env or your shell environment."
        )
    return database_url


def get_ai_engine() -> AsyncEngine:
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = create_async_engine(get_ai_database_url(), echo=True)
    return _ai_engine


def get_ai_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _ai_sessionmaker
    if _ai_sessionmaker is None:
        _ai_sessionmaker = async_sessionmaker(
            bind=get_ai_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _ai_sessionmaker


def get_ai_alembic_head_revision() -> str:
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "ai" / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "ai" / "alembic"))
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected exactly one AI Alembic head, found: {heads}")
    return heads[0]


def build_missing_ai_migration_error() -> str:
    return (
        f"AI database migrations are not applied. Missing or unreadable "
        f"{AI_ALEMBIC_VERSION_TABLE}. For an empty AI database run: "
        f"{AI_ALEMBIC_UPGRADE_COMMAND}. If ai_chat_history already exists and "
        f"matches the current schema, run: {AI_ALEMBIC_STAMP_COMMAND}"
    )


def build_ai_migration_revision_mismatch_error(
    current_revision: str | None,
    head_revision: str,
) -> str:
    current = current_revision or "<none>"
    return (
        "AI database migrations are not at head. "
        f"Current revision: {current}. Expected head: {head_revision}. Run: "
        f"{AI_ALEMBIC_UPGRADE_COMMAND}"
    )


def assert_ai_migration_revision_is_head(
    current_revision: str | None,
    head_revision: str,
) -> None:
    if current_revision != head_revision:
        raise RuntimeError(
            build_ai_migration_revision_mismatch_error(
                current_revision,
                head_revision,
            )
        )


async def verify_ai_migrations_applied() -> None:
    head_revision = get_ai_alembic_head_revision()
    try:
        async with get_ai_engine().begin() as conn:
            result = await conn.execute(
                text(f"SELECT version_num FROM {AI_ALEMBIC_VERSION_TABLE} LIMIT 1")
            )
            current_revision = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        raise RuntimeError(build_missing_ai_migration_error()) from exc
    assert_ai_migration_revision_is_head(current_revision, head_revision)


async def get_ai_db():
    async with get_ai_sessionmaker()() as session:
        yield session


async def init_ai_db() -> None:
    import ai.models.agent_artifact  # noqa: F401
    import ai.models.agent_memory  # noqa: F401
    import ai.models.agent_session  # noqa: F401
    import ai.models.agent_turn  # noqa: F401
    import ai.models.agent_turn_audit  # noqa: F401
    import ai.models.chat_history  # noqa: F401
    import ai.models.harness_event  # noqa: F401
    import ai.models.harness_run  # noqa: F401
    import ai.models.governance_state  # noqa: F401
    import ai.models.knowledge_chunk  # noqa: F401
    import ai.models.knowledge_document  # noqa: F401
    import ai.models.knowledge_job  # noqa: F401
    import ai.models.knowledge_section  # noqa: F401
    import ai.models.outbox_event  # noqa: F401

    await verify_ai_migrations_applied()
