from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_artifact import AgentArtifact
from ai.repositories.harness_repository import append_harness_event


def new_artifact_id() -> str:
    return str(uuid4())


async def write_artifact(
    db: AsyncSession,
    run_id: str,
    session_id: str,
    request_id: str | None,
    user_id: int,
    artifact_type: str,
    payload: dict[str, Any],
    now: datetime | None = None,
) -> AgentArtifact:
    current_time = now or datetime.now()
    artifact = AgentArtifact(
        artifact_id=new_artifact_id(),
        run_id=run_id,
        session_id=session_id,
        request_id=request_id,
        user_id=user_id,
        artifact_type=artifact_type,
        payload=payload,
        created_at=current_time,
    )
    db.add(artifact)
    await db.flush()
    await append_harness_event(
        db,
        run_id=run_id,
        event_type="artifact_written",
        payload={
            "artifact_id": artifact.artifact_id,
            "artifact_type": artifact_type,
        },
        now=current_time,
    )
    return artifact


async def list_artifacts(
    db: AsyncSession,
    *,
    run_id: str | None = None,
    session_id: str | None = None,
    request_id: str | None = None,
    user_id: int | None = None,
    artifact_type: str | None = None,
) -> list[AgentArtifact]:
    statement = select(AgentArtifact)
    if run_id is not None:
        statement = statement.where(AgentArtifact.run_id == run_id)
    if session_id is not None:
        statement = statement.where(AgentArtifact.session_id == session_id)
    if request_id is not None:
        statement = statement.where(AgentArtifact.request_id == request_id)
    if user_id is not None:
        statement = statement.where(AgentArtifact.user_id == user_id)
    if artifact_type is not None:
        statement = statement.where(AgentArtifact.artifact_type == artifact_type)
    statement = statement.order_by(AgentArtifact.created_at)

    result = await db.execute(statement)
    return list(result.scalars().all())
