import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ai.database import get_ai_sessionmaker
from ai.harness.errors import HarnessError
from ai.orchestrator.errors import OrchestratorError
from ai.orchestrator.schemas import AITurnCommand
from ai.orchestrator.service import handle_turn
from ai.prompts.character_service import DEFAULT_CHARACTER, normalize_character
from ai.repositories.agent_session_repository import (
    get_latest_active_session_for_user_character,
)
from ai.repositories.agent_turn_repository import (
    clear_user_agent_history,
    list_session_turns_for_user,
)
from ai.schemas.turn import AITurnHistoryItem, AITurnHistoryResponse, AITurnRequest, AITurnResponse
from common.dependencies import get_current_user_id

router = APIRouter(prefix="/ai", tags=["ai"])


def _normalize_history_limit(limit: int) -> int:
    return max(1, min(limit, 100))


def _sse_data(payload: str) -> str:
    return f"data: {payload}\n\n"


def _sse_event(event: str, payload: str) -> str:
    return f"event: {event}\ndata: {payload}\n\n"


def _chunk_text(text: str, size: int = 8) -> list[str]:
    if not text:
        return []
    return [text[index:index + size] for index in range(0, len(text), size)]


@router.post("/turn", response_model=AITurnResponse)
async def create_ai_turn(
    request: AITurnRequest,
    user_id: int = Depends(get_current_user_id),
):
    command = AITurnCommand(
        request_id=request.request_id,
        session_id=request.session_id,
        user_id=user_id,
        message=request.message,
        character=request.character,
        metadata=request.metadata or {},
    )
    try:
        result = await handle_turn(command)
    except OrchestratorError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"error_code": exc.error_code, "message": str(exc)},
        ) from exc
    except HarnessError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error_code": exc.error_code, "message": str(exc)},
        ) from exc
    return AITurnResponse(**result.to_payload())


@router.post("/turn/stream")
async def create_ai_turn_stream(
    request: AITurnRequest,
    user_id: int = Depends(get_current_user_id),
):
    command = AITurnCommand(
        request_id=request.request_id,
        session_id=request.session_id,
        user_id=user_id,
        message=request.message,
        character=request.character,
        metadata=request.metadata or {},
    )

    async def generate():
        try:
            result = await handle_turn(command)
            yield _sse_event("session", result.session_id)
            for chunk in _chunk_text(result.answer):
                yield _sse_data(chunk)
                await asyncio.sleep(0.02)
            yield _sse_data("[DONE]")
        except OrchestratorError as exc:
            payload = {
                "error_code": exc.error_code,
                "message": str(exc),
            }
            yield _sse_event("error", json.dumps(payload, ensure_ascii=False))
            yield _sse_data("[DONE]")
        except HarnessError as exc:
            payload = {
                "error_code": exc.error_code,
                "message": str(exc),
            }
            yield _sse_event("error", json.dumps(payload, ensure_ascii=False))
            yield _sse_data("[DONE]")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/turn/history", response_model=AITurnHistoryResponse)
async def get_ai_turn_history(
    character: str | None = None,
    limit: int = 30,
    before_sequence_no: int | None = None,
    user_id: int = Depends(get_current_user_id),
):
    actual_character = normalize_character(character or DEFAULT_CHARACTER)
    page_size = _normalize_history_limit(limit)
    async with get_ai_sessionmaker()() as db:
        session = await get_latest_active_session_for_user_character(
            db=db,
            user_id=user_id,
            character=actual_character,
        )
        if session is None:
            return AITurnHistoryResponse(
                session_id=None,
                items=[],
                has_more=False,
                next_before_sequence_no=None,
            )

        turns, has_more = await list_session_turns_for_user(
            db=db,
            session_id=session.session_id,
            user_id=user_id,
            limit=page_size,
            before_sequence_no=before_sequence_no,
        )

    return AITurnHistoryResponse(
        session_id=session.session_id,
        items=[
            AITurnHistoryItem(
                id=turn.id,
                role=turn.role,
                content=turn.content,
                character=turn.character,
                sequence_no=turn.sequence_no,
                created_at=turn.created_at,
            )
            for turn in turns
        ],
        has_more=has_more,
        next_before_sequence_no=turns[0].sequence_no if has_more and turns else None,
    )


@router.delete("/turn/history")
async def clear_ai_turn_history(
    character: str | None = None,
    user_id: int = Depends(get_current_user_id),
):
    actual_character = normalize_character(character or DEFAULT_CHARACTER)
    async with get_ai_sessionmaker()() as db:
        cleared_sessions, cleared_turns = await clear_user_agent_history(
            db=db,
            user_id=user_id,
            character=actual_character,
        )
        await db.commit()
    return {
        "cleared_sessions": cleared_sessions,
        "cleared_turns": cleared_turns,
    }
