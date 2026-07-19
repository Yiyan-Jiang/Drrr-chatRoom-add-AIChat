from sqlalchemy import select

from ai.database import get_ai_sessionmaker
from ai.memory.models import AgentMemoryItem, ConversationSummary
from ai.memory.repositories import create_agent_memory
from ai.models.agent_turn import AgentTurn
from ai.models.outbox_event import OutboxEvent


def refresh_summary(
    previous: ConversationSummary,
    turns: list,
) -> ConversationSummary:
    new_turns = [
        turn for turn in turns if turn.sequence_no > previous.source_last_sequence_no
    ]
    if not new_turns:
        return previous

    text = " ".join([previous.text] + [turn.content for turn in new_turns]).strip()
    return ConversationSummary(
        session_id=previous.session_id,
        text=text,
        source_last_sequence_no=max(turn.sequence_no for turn in new_turns),
    )


def extract_memory_for_turn(
    user_id: int,
    session_id: str,
    turn,
) -> list[AgentMemoryItem]:
    if turn.role != "user":
        return []

    content = str(turn.content).strip()
    memory_type = _classify_memory(content)
    if memory_type is None:
        return []

    return [
        AgentMemoryItem(
            user_id=user_id,
            session_id=session_id,
            memory_type=memory_type,
            content=content,
            source_sequence_no=turn.sequence_no,
            importance=5 if memory_type == "instruction" else 4,
            confidence=0.9,
        )
    ]


async def handle_memory_extract_requested(
    event: OutboxEvent,
    sessionmaker=None,
) -> None:
    payload = event.payload or {}
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    user_turn_id = payload.get("user_turn_id")
    character = payload.get("character")
    if user_id is None or session_id is None or user_turn_id is None:
        raise ValueError("memory extraction event is missing required payload fields")

    session_factory = sessionmaker or get_ai_sessionmaker()
    async with session_factory() as db:
        turn = await _get_agent_turn(db, user_turn_id)
        if turn is None:
            return
        for item in extract_memory_for_turn(
            user_id=user_id,
            session_id=session_id,
            turn=turn,
        ):
            await create_agent_memory(
                db=db,
                item=item,
                character=character,
                source_turn_id=turn.id,
            )
        await db.commit()


async def _get_agent_turn(db, turn_id: int) -> AgentTurn | None:
    records = getattr(db, "records", None)
    if records is not None:
        for record in records:
            if isinstance(record, AgentTurn) and record.id == turn_id:
                return record
        return None

    result = await db.execute(select(AgentTurn).where(AgentTurn.id == turn_id))
    return result.scalar_one_or_none()


def _classify_memory(content: str) -> str | None:
    lowered = content.lower()
    instruction_markers = (
        "\u4ee5\u540e",
        "\u4e4b\u540e",
        "\u4e0b\u6b21",
        "\u6bcf\u6b21",
        "\u603b\u662f",
        "\u4e0d\u8981",
        "\u8bf7\u5148",
        "\u5148\u7ed9",
        "\u786e\u8ba4\u540e",
        "always",
        "never",
    )
    preference_markers = (
        "\u559c\u6b22",
        "\u4e0d\u559c\u6b22",
        "\u504f\u597d",
        "\u4e60\u60ef",
        "prefer",
        "preference",
    )
    profile_markers = (
        "\u6211\u662f",
        "\u6211\u7684\u9879\u76ee",
        "\u6211\u5728\u505a",
        "my project",
        "i am",
        "i'm",
    )
    if any(marker in content or marker in lowered for marker in instruction_markers):
        return "instruction"
    if any(marker in content or marker in lowered for marker in preference_markers):
        return "preference"
    if any(marker in content or marker in lowered for marker in profile_markers):
        return "profile"
    return None
