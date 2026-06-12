from ai.orchestrator.errors import (
    PreviousRequestFailed,
    RequestIdOwnershipError,
    RequestInProgress,
)
from ai.orchestrator.schemas import AITurnResult
from ai.repositories.agent_audit_repository import RequestReservation


def resolve_reservation(reservation: RequestReservation) -> AITurnResult | None:
    if reservation.kind == "accepted":
        return None

    if reservation.kind == "completed":
        return AITurnResult.from_payload(reservation.response_payload)

    if reservation.kind == "in_progress":
        raise RequestInProgress("same request_id is still running")

    if reservation.kind == "denied":
        raise RequestIdOwnershipError("request_id belongs to another user")

    if reservation.kind == "failed":
        raise PreviousRequestFailed(reservation.error_code or "previous request failed")

    raise RuntimeError(f"unknown reservation kind: {reservation.kind}")
