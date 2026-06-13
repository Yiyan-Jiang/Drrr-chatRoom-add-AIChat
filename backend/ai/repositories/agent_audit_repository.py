from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models.agent_turn_audit import AgentTurnAudit


@dataclass(frozen=True)
class RequestReservation:
    kind: str
    audit: AgentTurnAudit | None = None
    response_payload: dict[str, Any] | None = None
    error_code: str | None = None


async def get_audit_by_request_id(
    db: AsyncSession,
    request_id: str,
) -> AgentTurnAudit | None:
    result = await db.execute(
        select(AgentTurnAudit).where(AgentTurnAudit.request_id == request_id)
    )
    return result.scalar_one_or_none()


def resolve_existing_audit(
    audit: AgentTurnAudit | None,
    user_id: int,
) -> RequestReservation:
    if audit is None:
        return RequestReservation(kind="conflict")

    if audit.user_id != user_id:
        return RequestReservation(kind="denied")

    if audit.status == "completed":
        return RequestReservation(
            kind="completed",
            audit=audit,
            response_payload=audit.response_payload,
        )

    if audit.status in ("pending", "running"):
        return RequestReservation(kind="in_progress", audit=audit)

    if audit.status == "failed":
        return RequestReservation(kind="failed", audit=audit, error_code=audit.error_code)

    return RequestReservation(kind="unknown", audit=audit)


async def reserve_request(
    db: AsyncSession,
    request_id: str,
    user_id: int,
    session_id: str | None,
    now: datetime | None = None,
) -> RequestReservation:
    current_time = now or datetime.now()
    audit = AgentTurnAudit(
        request_id=request_id,
        user_id=user_id,
        session_id=session_id,
        status="pending",
        stage="reserved",
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(audit)

    try:
        await db.commit()
        await db.refresh(audit)
        return RequestReservation(kind="accepted", audit=audit)
    except IntegrityError:
        await db.rollback()
        existing = await get_audit_by_request_id(db, request_id)
        return resolve_existing_audit(existing, user_id)


async def mark_audit_running(
    db: AsyncSession,
    request_id: str,
    stage: str,
    now: datetime | None = None,
) -> AgentTurnAudit:
    audit = await get_audit_by_request_id(db, request_id)
    if audit is None:
        raise ValueError(f"Audit not found for request_id={request_id}")

    current_time = now or datetime.now()
    audit.status = "running"
    audit.stage = stage
    audit.updated_at = current_time
    await db.flush()
    return audit


async def mark_audit_completed(
    db: AsyncSession,
    request_id: str,
    response_payload: dict[str, Any],
    now: datetime | None = None,
) -> AgentTurnAudit:
    audit = await get_audit_by_request_id(db, request_id)
    if audit is None:
        raise ValueError(f"Audit not found for request_id={request_id}")

    current_time = now or datetime.now()
    audit.status = "completed"
    audit.stage = "completed"
    audit.response_payload = response_payload
    audit.error_code = None
    audit.error_message = None
    audit.updated_at = current_time
    audit.completed_at = current_time
    await db.flush()
    return audit


async def mark_audit_failed(
    db: AsyncSession,
    request_id: str,
    error_code: str,
    error_message: str,
    debug_payload: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> AgentTurnAudit:
    audit = await get_audit_by_request_id(db, request_id)
    if audit is None:
        raise ValueError(f"Audit not found for request_id={request_id}")

    current_time = now or datetime.now()
    audit.status = "failed"
    audit.stage = "failed"
    audit.error_code = error_code
    audit.error_message = error_message
    audit.debug_payload = debug_payload
    audit.updated_at = current_time
    await db.flush()
    return audit
