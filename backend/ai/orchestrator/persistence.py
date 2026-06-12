from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_session import AgentSession
from ai.orchestrator.schemas import AITurnCommand, AITurnResult, RunResult
from ai.repositories.agent_audit_repository import mark_audit_completed
from ai.repositories.agent_turn_repository import append_turn_pair_to_locked_session
from ai.repositories.outbox_repository import create_outbox_event


async def persist_success(
    db: AsyncSession,
    command: AITurnCommand,
    session: AgentSession,
    run_result: RunResult,
    response: AITurnResult,
    now: datetime | None = None,
) -> None:
    current_time = now or datetime.now()
    user_turn, assistant_turn = await append_turn_pair_to_locked_session(
        db=db,
        session=session,
        request_id=command.request_id,
        user_content=command.message,
        assistant_content=run_result.answer,
        character=command.character,
        now=current_time,
    )
    await create_outbox_event(
        db=db,
        event_type="turn_completed",
        aggregate_type="session",
        aggregate_id=session.session_id,
        payload={
            "session_id": session.session_id,
            "request_id": command.request_id,
            "user_turn_id": user_turn.id,
            "assistant_turn_id": assistant_turn.id,
        },
        now=current_time,
    )
    await mark_audit_completed(
        db=db,
        request_id=command.request_id,
        response_payload=response.to_payload(),
        now=current_time,
    )
