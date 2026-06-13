from collections.abc import Callable
from dataclasses import dataclass, field

from ai.config.model_routes import ModelRoute


@dataclass(frozen=True)
class RoutePolicy:
    compact_context: bool = False
    allow_fallback: bool = False
    disable_rerank: bool = False
    force_local: bool = False
    force_cheaper_model: bool = False
    local_fallback_route: ModelRoute | None = None
    cheaper_routes: dict[str, ModelRoute] = field(default_factory=dict)
    fallback_routes: dict[str, ModelRoute] = field(default_factory=dict)
    unhealthy_providers: list[str] = field(default_factory=list)
    reason: str | None = None


def choose_model(
    *,
    task_type: str,
    character: str | None,
    policy: RoutePolicy,
    resolver: Callable[[str | None, str], ModelRoute],
) -> ModelRoute:
    if policy.force_local and policy.local_fallback_route is not None:
        return policy.local_fallback_route

    if policy.force_cheaper_model and task_type in policy.cheaper_routes:
        return policy.cheaper_routes[task_type]

    route = resolver(character, task_type)
    if (
        policy.allow_fallback
        and route.provider in set(policy.unhealthy_providers)
        and task_type in policy.fallback_routes
    ):
        return policy.fallback_routes[task_type]

    return route
