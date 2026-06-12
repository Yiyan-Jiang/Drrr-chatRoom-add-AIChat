from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.database import get_ai_sessionmaker
from ai.models.agent_artifact import AgentArtifact
from ai.models.harness_event import HarnessEvent
from ai.models.harness_run import HarnessRun


def new_run_id() -> str:
    return str(uuid4())


async def append_harness_event(
    db: AsyncSession,
    run_id: str,
    event_type: str,
    payload: dict[str, Any],
    now: datetime | None = None,
) -> HarnessEvent:
    result = await db.execute(
        select(HarnessEvent)
        .where(HarnessEvent.run_id == run_id)
        .order_by(HarnessEvent.sequence_no.desc())
        .limit(1)
    )
    existing_events = [
        event for event in result.scalars().all() if hasattr(event, "sequence_no")
    ]
    last_sequence = max((event.sequence_no for event in existing_events), default=0)
    event = HarnessEvent(
        run_id=run_id,
        sequence_no=last_sequence + 1,
        event_type=event_type,
        payload=payload,
        created_at=now or datetime.now(),
    )
    db.add(event)
    await db.flush()
    return event


async def update_run_checkpoint(
    db: AsyncSession,
    run: HarnessRun,
    checkpoint: dict[str, Any],
    now: datetime | None = None,
) -> HarnessRun:
    run.checkpoint_payload = checkpoint
    run.updated_at = now or datetime.now()
    await db.flush()
    return run


class SqlAlchemyHarnessRepository:
    def __init__(self, sessionmaker=None):
        self._sessionmaker = sessionmaker or get_ai_sessionmaker()

    async def load_or_create_run(self, workspace) -> HarnessRun:
        async with self._sessionmaker() as db:
            result = await db.execute(
                select(HarnessRun).where(
                    HarnessRun.session_id == workspace.session.session_id,
                    HarnessRun.request_id == workspace.command.request_id,
                )
            )
            run = result.scalar_one_or_none()
            if run is not None:
                return run

            current_time = datetime.now()
            run = HarnessRun(
                run_id=new_run_id(),
                session_id=workspace.session.session_id,
                request_id=workspace.command.request_id,
                user_id=workspace.command.user_id,
                status="created",
                checkpoint_payload=None,
                skill_state_payload=None,
                created_at=current_time,
                updated_at=current_time,
            )
            db.add(run)
            await db.commit()
            await db.refresh(run)
            return run

    async def list_events(self, run_id: str) -> list[HarnessEvent]:
        async with self._sessionmaker() as db:
            result = await db.execute(
                select(HarnessEvent)
                .where(HarnessEvent.run_id == run_id)
                .order_by(HarnessEvent.sequence_no)
            )
            return list(result.scalars().all())

    async def list_artifacts(self, run_id: str) -> list[AgentArtifact]:
        async with self._sessionmaker() as db:
            result = await db.execute(
                select(AgentArtifact).where(AgentArtifact.run_id == run_id)
            )
            return list(result.scalars().all())

    async def append_event(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> HarnessEvent:
        async with self._sessionmaker() as db:
            event = await append_harness_event(db, run_id, event_type, payload)
            await db.commit()
            await db.refresh(event)
            return event

    async def update_checkpoint(self, run: HarnessRun, checkpoint: dict[str, Any]) -> HarnessRun:
        async with self._sessionmaker() as db:
            merged = await db.merge(run)
            updated = await update_run_checkpoint(db, merged, checkpoint)
            await db.commit()
            await db.refresh(updated)
            return updated

    async def update_skill_state(
        self,
        run: HarnessRun,
        skill_state: dict[str, Any],
    ) -> HarnessRun:
        async with self._sessionmaker() as db:
            merged = await db.merge(run)
            merged.skill_state_payload = skill_state
            merged.updated_at = datetime.now()
            await db.commit()
            await db.refresh(merged)
            run.skill_state_payload = skill_state
            return merged

    async def mark_terminal(self, run: HarnessRun, status: str) -> HarnessRun:
        async with self._sessionmaker() as db:
            merged = await db.merge(run)
            merged.status = status
            merged.completed_at = datetime.now()
            merged.updated_at = merged.completed_at
            await db.commit()
            await db.refresh(merged)
            return merged

    async def mark_failed(
        self,
        run: HarnessRun,
        error_code: str,
        error_message: str,
    ) -> HarnessRun:
        async with self._sessionmaker() as db:
            merged = await db.merge(run)
            merged.status = "failed"
            merged.error_code = error_code
            merged.error_message = error_message
            merged.updated_at = datetime.now()
            await db.commit()
            await db.refresh(merged)
            return merged

    async def write_artifact(
        self,
        run: HarnessRun,
        artifact_type: str,
        payload: dict[str, Any],
        request_id: str | None = None,
    ) -> AgentArtifact:
        from ai.repositories.artifact_repository import write_artifact

        async with self._sessionmaker() as db:
            artifact = await write_artifact(
                db,
                run_id=run.run_id,
                session_id=run.session_id,
                request_id=request_id or run.request_id,
                user_id=run.user_id,
                artifact_type=artifact_type,
                payload=payload,
            )
            await db.commit()
            await db.refresh(artifact)
            return artifact
