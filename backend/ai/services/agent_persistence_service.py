from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ai.repositories.agent_audit_repository import mark_audit_completed
from ai.repositories.agent_session_repository import get_agent_session_for_update
from ai.repositories.agent_turn_repository import append_turn_pair_to_locked_session
from ai.repositories.outbox_repository import create_outbox_event


async def persist_completed_turn(
    db: AsyncSession,
    session_id: str,
    user_id: int,
    request_id: str,
    user_content: str,
    assistant_content: str,
    response_payload: dict[str, Any],
    character: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = now or datetime.now()

    async with db.begin():
        session = await get_agent_session_for_update(db, session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        if session.user_id != user_id:
            raise PermissionError("session belongs to another user")

        user_turn, assistant_turn = await append_turn_pair_to_locked_session(
            db=db,
            session=session,
            request_id=request_id,
            user_content=user_content,
            assistant_content=assistant_content,
            character=character,
            now=current_time,
        )

        outbox = await create_outbox_event(
            db=db,
            event_type="turn_completed",
            aggregate_type="session",
            aggregate_id=session_id,
            payload={
                "session_id": session_id,
                "request_id": request_id,
                "user_turn_id": user_turn.id,
                "assistant_turn_id": assistant_turn.id,
            },
            now=current_time,
        )

        audit = await mark_audit_completed(
            db=db,
            request_id=request_id,
            response_payload=response_payload,
            now=current_time,
        )

    return {
        "session_id": session_id,
        "request_id": request_id,
        "user_turn_id": user_turn.id,
        "assistant_turn_id": assistant_turn.id,
        "outbox_event_id": outbox.event_id,
        "audit_status": audit.status,
    }
