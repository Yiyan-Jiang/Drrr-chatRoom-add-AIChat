from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn
from ai.repositories.agent_session_repository import get_agent_session_for_update


async def list_recent_turns(
    db: AsyncSession,
    session_id: str,
    limit: int = 20,
) -> list[AgentTurn]:
    result = await db.execute(
        select(AgentTurn)
        .where(AgentTurn.session_id == session_id)
        .order_by(AgentTurn.sequence_no.desc())
        .limit(limit)
    )
    turns = list(result.scalars().all())
    turns.reverse()
    return turns


async def list_session_turns_for_user(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    limit: int,
    before_sequence_no: int | None = None,
) -> tuple[list[AgentTurn], bool]:
    page_size = max(1, min(limit, 100))
    query = (
        select(AgentTurn)
        .where(
            AgentTurn.session_id == session_id,
            AgentTurn.user_id == user_id,
        )
        .order_by(AgentTurn.sequence_no.desc())
        .limit(page_size + 1)
    )
    if before_sequence_no is not None:
        query = query.where(AgentTurn.sequence_no < before_sequence_no)

    result = await db.execute(query)
    records = list(result.scalars().all())
    has_more = len(records) > page_size
    page = records[:page_size]
    page.reverse()
    return page, has_more


async def clear_user_agent_history(
    db: AsyncSession,
    user_id: int,
    character: str,
) -> tuple[int, int]:
    session_result = await db.execute(
        select(AgentSession.session_id)
        .join(AgentTurn, AgentTurn.session_id == AgentSession.session_id)
        .where(
            AgentSession.user_id == user_id,
            AgentTurn.user_id == user_id,
            AgentTurn.character == character,
        )
        .distinct()
    )
    session_ids = list(session_result.scalars().all())
    if not session_ids:
        return 0, 0

    turns_result = await db.execute(
        delete(AgentTurn).where(
            AgentTurn.user_id == user_id,
            AgentTurn.session_id.in_(session_ids),
            AgentTurn.character == character,
        )
    )
    sessions_result = await db.execute(
        delete(AgentSession).where(
            AgentSession.user_id == user_id,
            AgentSession.session_id.in_(session_ids),
        )
    )
    return sessions_result.rowcount or 0, turns_result.rowcount or 0


async def append_turn_pair(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    request_id: str,
    user_content: str,
    assistant_content: str,
    character: str | None = None,
    now: datetime | None = None,
) -> tuple[AgentTurn, AgentTurn]:
    session = await get_agent_session_for_update(db, session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")
    if session.user_id != user_id:
        raise PermissionError("session belongs to another user")

    return await append_turn_pair_to_locked_session(
        db=db,
        session=session,
        request_id=request_id,
        user_content=user_content,
        assistant_content=assistant_content,
        character=character,
        now=now,
    )


async def append_turn_pair_to_locked_session(
    db: AsyncSession,
    session: AgentSession,
    request_id: str,
    user_content: str,
    assistant_content: str,
    character: str | None = None,
    now: datetime | None = None,
) -> tuple[AgentTurn, AgentTurn]:
    current_time = now or datetime.now()
    user_seq = session.last_sequence_no + 1
    assistant_seq = session.last_sequence_no + 2

    user_turn = AgentTurn(
        session_id=session.session_id,
        user_id=session.user_id,
        sequence_no=user_seq,
        role="user",
        content=user_content,
        request_id=request_id,
        character=character,
        created_at=current_time,
    )
    assistant_turn = AgentTurn(
        session_id=session.session_id,
        user_id=session.user_id,
        sequence_no=assistant_seq,
        role="assistant",
        content=assistant_content,
        request_id=request_id,
        character=character,
        created_at=current_time,
    )

    session.last_sequence_no = assistant_seq
    session.updated_at = current_time

    db.add(user_turn)
    db.add(assistant_turn)
    await db.flush()
    return user_turn, assistant_turn
