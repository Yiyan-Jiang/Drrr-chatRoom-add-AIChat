from datetime import datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.chat_history import AIChatHistory


async def create_ai_chat_history(
    db: AsyncSession, user_id: int, role: str, content: str, character: str = "sakura"
) -> AIChatHistory:
    record = AIChatHistory(
        user_id=user_id,
        character=character,
        role=role,
        content=content,
        created_at=datetime.now(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_user_ai_chat_history(
    db: AsyncSession, user_id: int, limit: int = 8, character: str = "sakura"
) -> List[AIChatHistory]:
    res = await db.execute(
        select(AIChatHistory)
        .where(
            AIChatHistory.user_id == user_id,
            AIChatHistory.character == character,
        )
        .order_by(AIChatHistory.created_at.desc())
        .limit(limit)
    )
    records = list(res.scalars().all())
    records.reverse()
    return records


async def delete_all_ai_chat_history(
    db: AsyncSession, user_id: int, character: str = "sakura"
) -> int:
    res = await db.execute(
        select(AIChatHistory).where(
            AIChatHistory.user_id == user_id,
            AIChatHistory.character == character,
        )
    )
    records = res.scalars().all()
    count = len(records)
    for record in records:
        await db.delete(record)
    if count > 0:
        await db.commit()
    return count
