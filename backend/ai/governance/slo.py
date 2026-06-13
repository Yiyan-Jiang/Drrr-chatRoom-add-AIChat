from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseSlo:
    max_error_rate: float
    max_invalid_action_rate: float


@dataclass(frozen=True)
class RolloutMetrics:
    error_rate: float
    planner_invalid_action_rate: float


@dataclass(frozen=True)
class RolloutEvaluation:
    release_id: str
    action: str
    reason: str


def evaluate_rollout(
    *,
    release_id: str,
    slo: ReleaseSlo,
    metrics: RolloutMetrics,
) -> RolloutEvaluation:
    if metrics.error_rate > slo.max_error_rate:
        return RolloutEvaluation(
            release_id=release_id,
            action="rollback",
            reason="error_rate exceeded",
        )
    if metrics.planner_invalid_action_rate > slo.max_invalid_action_rate:
        return RolloutEvaluation(
            release_id=release_id,
            action="rollback",
            reason="planner_invalid_action_rate exceeded",
        )
    return RolloutEvaluation(
        release_id=release_id,
        action="continue",
        reason="within_slo",
    )
