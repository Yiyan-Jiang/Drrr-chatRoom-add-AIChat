from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.memory.models import AgentMemoryItem
from ai.models.agent_memory import AgentMemory
from ai.models.outbox_event import OutboxEvent


def new_memory_id() -> str:
    return str(uuid4())


def _session_records(db) -> list | None:
    return getattr(db, "records", None)


async def create_agent_memory(
    db: AsyncSession,
    item: AgentMemoryItem,
    character: str | None,
    source_turn_id: int | None = None,
    now: datetime | None = None,
) -> AgentMemory:
    current_time = now or datetime.now()
    existing = await _find_existing_source_memory(
        db=db,
        user_id=item.user_id,
        character=character,
        source_turn_id=source_turn_id,
        memory_type=item.memory_type,
    )
    if existing is not None:
        existing.content = item.content
        existing.source_sequence_no = item.source_sequence_no
        existing.importance = item.importance
        existing.confidence = item.confidence
        existing.status = "active"
        existing.updated_at = current_time
        await db.flush()
        return existing

    record = AgentMemory(
        memory_id=new_memory_id(),
        user_id=item.user_id,
        character=character,
        session_id=item.session_id,
        source_turn_id=source_turn_id,
        source_sequence_no=item.source_sequence_no,
        memory_type=item.memory_type,
        content=item.content,
        importance=item.importance,
        confidence=item.confidence,
        status="active",
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(record)
    await db.flush()
    return record


async def _find_existing_source_memory(
    db: AsyncSession,
    user_id: int,
    character: str | None,
    source_turn_id: int | None,
    memory_type: str,
) -> AgentMemory | None:
    if source_turn_id is None:
        return None

    records = _session_records(db)
    if records is not None:
        for record in records:
            if (
                isinstance(record, AgentMemory)
                and record.user_id == user_id
                and record.character == character
                and record.source_turn_id == source_turn_id
                and record.memory_type == memory_type
            ):
                return record
        return None

    result = await db.execute(
        select(AgentMemory).where(
            AgentMemory.user_id == user_id,
            AgentMemory.character == character,
            AgentMemory.source_turn_id == source_turn_id,
            AgentMemory.memory_type == memory_type,
        )
    )
    return result.scalar_one_or_none()


async def list_relevant_memories(
    db: AsyncSession,
    user_id: int,
    character: str | None,
    query: str,
    limit: int = 8,
    now: datetime | None = None,
) -> list[AgentMemory]:
    records = _session_records(db)
    if records is not None:
        memories = [
            record
            for record in records
            if isinstance(record, AgentMemory)
            and record.user_id == user_id
            and record.character == character
            and record.status == "active"
        ]
    else:
        result = await db.execute(
            select(AgentMemory)
            .where(
                AgentMemory.user_id == user_id,
                AgentMemory.character == character,
                AgentMemory.status == "active",
            )
            .order_by(
                AgentMemory.importance.desc(),
                AgentMemory.updated_at.desc(),
            )
            .limit(max(1, min(limit, 20)))
        )
        memories = list(result.scalars().all())

    ranked = sorted(
        memories,
        key=lambda memory: (
            _lexical_overlap(query, memory.content),
            memory.importance,
            memory.updated_at or datetime.min,
        ),
        reverse=True,
    )[: max(1, min(limit, 20))]

    current_time = now or datetime.now()
    for memory in ranked:
        memory.last_used_at = current_time
    return ranked


async def clear_user_agent_memory(
    db: AsyncSession,
    user_id: int,
    character: str,
) -> tuple[int, int]:
    records = _session_records(db)
    if records is not None:
        before = len(records)
        db.records = [
            record
            for record in records
            if not (
                isinstance(record, AgentMemory)
                and record.user_id == user_id
                and record.character == character
            )
        ]
        memory_count = before - len(db.records)
        before = len(db.records)
        db.records = [
            record
            for record in db.records
            if not (
                isinstance(record, OutboxEvent)
                and record.event_type == "ai_memory_extract_requested"
                and record.status in ("pending", "locked")
                and record.payload.get("user_id") == user_id
                and record.payload.get("character") == character
            )
        ]
        event_count = before - len(db.records)
        return memory_count, event_count

    memory_result = await db.execute(
        delete(AgentMemory).where(
            AgentMemory.user_id == user_id,
            AgentMemory.character == character,
        )
    )
    event_result = await db.execute(
        delete(OutboxEvent).where(
            OutboxEvent.event_type == "ai_memory_extract_requested",
            OutboxEvent.status.in_(("pending", "locked")),
            OutboxEvent.payload["user_id"].as_integer() == user_id,
            OutboxEvent.payload["character"].as_string() == character,
        )
    )
    return memory_result.rowcount or 0, event_result.rowcount or 0


def _lexical_overlap(query: str, content: str) -> int:
    query_terms = _terms(query)
    if not query_terms:
        return 0
    content_terms = _terms(content)
    return len(query_terms & content_terms)


def _terms(text: str) -> set[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    terms = {term for term in normalized.split() if len(term) >= 2}
    if terms:
        return terms
    return {text[index : index + 2] for index in range(max(0, len(text) - 1))}
