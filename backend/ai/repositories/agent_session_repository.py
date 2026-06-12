from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn


def new_session_id() -> str:
    return str(uuid4())


async def create_agent_session(
    db: AsyncSession,
    user_id: int,
    session_id: str | None = None,
    title: str | None = None,
    now: datetime | None = None,
) -> AgentSession:
    current_time = now or datetime.now()
    session = AgentSession(
        session_id=session_id or new_session_id(),
        user_id=user_id,
        title=title,
        status="active",
        last_sequence_no=0,
        summary_version=0,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(session)
    await db.flush()
    return session


async def get_agent_session_by_session_id(
    db: AsyncSession,
    session_id: str,
) -> AgentSession | None:
    result = await db.execute(
        select(AgentSession).where(AgentSession.session_id == session_id)
    )
    return result.scalar_one_or_none()


async def get_agent_session_for_update(
    db: AsyncSession,
    session_id: str,
) -> AgentSession | None:
    result = await db.execute(
        select(AgentSession)
        .where(AgentSession.session_id == session_id)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def list_user_sessions(
    db: AsyncSession,
    user_id: int,
    limit: int = 50,
) -> list[AgentSession]:
    result = await db.execute(
        select(AgentSession)
        .where(AgentSession.user_id == user_id)
        .order_by(AgentSession.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_latest_active_session_for_user_character(
    db: AsyncSession,
    user_id: int,
    character: str,
) -> AgentSession | None:
    result = await db.execute(
        select(AgentSession)
        .join(AgentTurn, AgentTurn.session_id == AgentSession.session_id)
        .where(
            AgentSession.user_id == user_id,
            AgentSession.status == "active",
            AgentTurn.user_id == user_id,
            AgentTurn.character == character,
        )
        .order_by(AgentTurn.created_at.desc(), AgentTurn.sequence_no.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def archive_agent_session(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    now: datetime | None = None,
) -> AgentSession:
    session = await get_agent_session_by_session_id(db, session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")
    if session.user_id != user_id:
        raise PermissionError("session belongs to another user")

    current_time = now or datetime.now()
    session.status = "archived"
    session.updated_at = current_time
    await db.flush()
    return session
