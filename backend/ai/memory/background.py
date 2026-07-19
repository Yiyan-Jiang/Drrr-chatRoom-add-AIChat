from sqlalchemy import select

from ai.database import get_ai_sessionmaker
from ai.models.agent_turn import AgentTurn
from ai.repositories.outbox_repository import create_outbox_event


async def enqueue_memory_extraction_for_request(
    request_id: str,
    user_id: int,
    session_id: str,
    character: str | None,
    sessionmaker=None,
) -> None:
    try:
        session_factory = sessionmaker or get_ai_sessionmaker()
        async with session_factory() as db:
            user_turn, assistant_turn = await _load_turn_pair_for_request(
                db=db,
                request_id=request_id,
                user_id=user_id,
                session_id=session_id,
                character=character,
            )
            if user_turn is None or assistant_turn is None:
                return

            await create_outbox_event(
                db=db,
                event_type="ai_memory_extract_requested",
                aggregate_type="session",
                aggregate_id=session_id,
                payload={
                    "session_id": session_id,
                    "request_id": request_id,
                    "user_id": user_id,
                    "character": character,
                    "user_turn_id": user_turn.id,
                    "assistant_turn_id": assistant_turn.id,
                },
            )
            await db.commit()
    except Exception:
        return


async def _load_turn_pair_for_request(
    db,
    request_id: str,
    user_id: int,
    session_id: str,
    character: str | None,
) -> tuple[AgentTurn | None, AgentTurn | None]:
    records = getattr(db, "records", None)
    if records is not None:
        turns = [
            record
            for record in records
            if isinstance(record, AgentTurn)
            and record.request_id == request_id
            and record.user_id == user_id
            and record.session_id == session_id
            and record.character == character
        ]
    else:
        result = await db.execute(
            select(AgentTurn)
            .where(
                AgentTurn.request_id == request_id,
                AgentTurn.user_id == user_id,
                AgentTurn.session_id == session_id,
                AgentTurn.character == character,
            )
            .order_by(AgentTurn.sequence_no)
        )
        turns = list(result.scalars().all())

    user_turn = next((turn for turn in turns if turn.role == "user"), None)
    assistant_turn = next((turn for turn in turns if turn.role == "assistant"), None)
    return user_turn, assistant_turn
