from typing import AsyncGenerator

from ai.config.model_routes import resolve_model_route
from ai.database import get_ai_sessionmaker
from ai.prompts.character_service import (
    DEFAULT_CHARACTER,
    get_allowed_characters,
    get_system_prompt,
    normalize_character,
)
from ai.providers.registry import get_provider
from ai.repositories.chat_history_repository import (
    create_ai_chat_history,
    get_user_ai_chat_history,
)

ALLOWED_CHARACTERS = get_allowed_characters()


async def _build_messages_with_history(
    user_id: int, user_message: str, character: str = DEFAULT_CHARACTER
) -> list[dict]:
    actual_character = normalize_character(character)
    messages = [{"role": "system", "content": get_system_prompt(actual_character)}]

    async with get_ai_sessionmaker()() as db:
        history = await get_user_ai_chat_history(
            db, user_id, limit=8, character=actual_character
        )
        for record in history:
            messages.append({"role": record.role, "content": record.content})

    messages.append({"role": "user", "content": user_message})
    return messages


async def chat_stream(
    user_id: int, user_message: str, character: str = DEFAULT_CHARACTER
) -> AsyncGenerator[str, None]:
    if character not in ALLOWED_CHARACTERS:
        yield f"data: error: unsupported character '{character}'\n\n"
        yield "data: [DONE]\n\n"
        return

    try:
        route = resolve_model_route(character=character, task_type="chat")
        provider = get_provider(route.provider)
        client = provider.create_client()
        messages = await _build_messages_with_history(user_id, user_message, character)

        stream = await client.chat.completions.create(
            model=route.model,
            messages=messages,
            max_tokens=256,
            stream=True,
        )

        full_content = ""
        async for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:
                full_content += content
                yield content

        yield "data: [DONE]\n\n"

        if full_content:
            async with get_ai_sessionmaker()() as db:
                await create_ai_chat_history(
                    db, user_id, "user", user_message, character
                )
                await create_ai_chat_history(
                    db, user_id, "assistant", full_content, character
                )

    except Exception as e:
        error_msg = str(e).replace("\n", " ")
        yield f"data: error: {error_msg}\n\n"
        yield "data: [DONE]\n\n"
