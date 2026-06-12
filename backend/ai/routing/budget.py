from dataclasses import dataclass

from ai.routing.policy import RoutePolicy


@dataclass(frozen=True)
class RunBudget:
    remaining_tokens: int
    remaining_cost_usd: float


def build_route_policy(budget: RunBudget, task_type: str) -> RoutePolicy:
    if budget.remaining_tokens < 2000:
        return RoutePolicy(
            compact_context=True,
            allow_fallback=True,
            disable_rerank=True,
            reason=f"{task_type}:low_tokens",
        )
    if budget.remaining_cost_usd < 0.01:
        return RoutePolicy(
            compact_context=True,
            force_cheaper_model=True,
            allow_fallback=True,
            reason=f"{task_type}:low_cost",
        )
    return RoutePolicy(reason=f"{task_type}:normal")
