from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ai.database import get_ai_sessionmaker
from ai.prompts.character_service import normalize_character
from ai.repositories.chat_history_repository import delete_all_ai_chat_history
from ai.schemas.chat import AIChatRequest
from ai.services.chat_service import chat_stream
from common.dependencies import get_current_user_id

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
async def chat(
    request: AIChatRequest,
    user_id: int = Depends(get_current_user_id),
):
    character = normalize_character(request.character)

    async def generate():
        async for chunk in chat_stream(user_id, request.message, character):
            if chunk.startswith("data: "):
                yield chunk
            elif "\n" in chunk:
                lines = chunk.split("\n")
                for i, line in enumerate(lines):
                    if i == len(lines) - 1 and not line:
                        continue
                    yield f"data: {line}\n"
                yield "\n"
            else:
                yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/chat/history")
async def clear_history(
    character: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
):
    actual_character = normalize_character(character)
    async with get_ai_sessionmaker()() as db:
        count = await delete_all_ai_chat_history(
            db, user_id=user_id, character=actual_character
        )
    return {"message": f"cleared {count} history records ({actual_character})"}
