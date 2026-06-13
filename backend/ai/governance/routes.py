from dataclasses import dataclass, field

from ai.routing.budget import RunBudget


@dataclass(frozen=True)
class GovernedRoute:
    rule_id: str
    task_type: str
    provider: str
    model: str
    character: str | None = None
    cost_rank: int = 100


@dataclass(frozen=True)
class RouteSet:
    route_set_id: str
    routes: list[GovernedRoute] = field(default_factory=list)
    fallback_routes: list[GovernedRoute] = field(default_factory=list)


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    provider: str
    model: str
    route_set_id: str
    rule_id: str
    fallback: bool
    reason: str

    def to_event(self) -> dict:
        return {
            "event_type": "model_route_decision",
            "payload": {
                "task_type": self.task_type,
                "provider": self.provider,
                "model": self.model,
                "route_set_id": self.route_set_id,
                "rule_id": self.rule_id,
                "fallback": self.fallback,
                "reason": self.reason,
            },
        }


def _matches(route: GovernedRoute, task_type: str, character: str | None) -> bool:
    if route.task_type != task_type:
        return False
    return route.character is None or route.character == character


def select_model_route(
    *,
    task_type: str,
    character: str | None,
    user_id: int,
    workspace_id: str | None,
    budget: RunBudget,
    route_set: RouteSet,
    unhealthy_providers: set[str] | None = None,
) -> RouteDecision:
    unhealthy = unhealthy_providers or set()
    candidates = [
        route for route in route_set.routes if _matches(route, task_type, character)
    ]
    healthy = [route for route in candidates if route.provider not in unhealthy]
    if budget.remaining_tokens < 2000 or budget.remaining_cost_usd < 0.01:
        healthy = sorted(healthy, key=lambda route: route.cost_rank)

    if healthy:
        selected = healthy[0]
        return RouteDecision(
            task_type=task_type,
            provider=selected.provider,
            model=selected.model,
            route_set_id=route_set.route_set_id,
            rule_id=selected.rule_id,
            fallback=False,
            reason=f"matched route set {route_set.route_set_id}",
        )

    fallbacks = [
        route
        for route in route_set.fallback_routes
        if _matches(route, task_type, character) and route.provider not in unhealthy
    ]
    if not fallbacks:
        raise ValueError(f"no healthy route for task_type: {task_type}")
    selected = fallbacks[0]
    return RouteDecision(
        task_type=task_type,
        provider=selected.provider,
        model=selected.model,
        route_set_id=route_set.route_set_id,
        rule_id=selected.rule_id,
        fallback=True,
        reason=f"fallback because primary providers were unhealthy for {task_type}",
    )
