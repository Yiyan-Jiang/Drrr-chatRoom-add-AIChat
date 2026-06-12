from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_session import AgentSession
from ai.orchestrator.errors import SessionNotActive, SessionNotFound, SessionOwnershipError
from ai.orchestrator.schemas import AITurnCommand
from ai.repositories.agent_session_repository import (
    create_agent_session,
    get_agent_session_by_session_id,
)


async def load_or_create_session_for_turn(
    db: AsyncSession,
    command: AITurnCommand,
) -> AgentSession:
    if command.session_id is None:
        session = await create_agent_session(db, user_id=command.user_id)
        await db.commit()
        await db.refresh(session)
        return session

    session = await get_agent_session_by_session_id(db, command.session_id)
    if session is None:
        raise SessionNotFound(f"Session not found: {command.session_id}")

    if session.user_id != command.user_id:
        raise SessionOwnershipError("session belongs to another user")

    if session.status != "active":
        raise SessionNotActive(f"Session is not active: {command.session_id}")

    return session
