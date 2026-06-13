import os
from dataclasses import dataclass


class PlannerModelConfigError(ValueError):
    pass


@dataclass(frozen=True)
class PlannerModelConfig:
    api_key: str
    base_url: str | None
    model: str
    max_tokens: int = 1024
    timeout_seconds: float = 30.0


def load_planner_model_config() -> PlannerModelConfig:
    api_key = os.environ.get("AGENT_CORE_MODEL_API_KEY") or os.environ.get(
        "DEEPSEEK_API_KEY"
    )
    if not api_key:
        raise PlannerModelConfigError(
            "AGENT_CORE_MODEL_API_KEY or DEEPSEEK_API_KEY is not set"
        )

    model = os.environ.get("AGENT_CORE_PLANNER_MODEL") or "deepseek-chat"
    if not model:
        raise PlannerModelConfigError("AGENT_CORE_PLANNER_MODEL is not set")

    return PlannerModelConfig(
        api_key=api_key,
        base_url=os.environ.get("AGENT_CORE_MODEL_BASE_URL")
        or os.environ.get("DEEPSEEK_BASE_URL")
        or "https://api.deepseek.com",
        model=model,
        max_tokens=_read_int("AGENT_CORE_PLANNER_MAX_TOKENS", default=1024),
        timeout_seconds=_read_float(
            "AGENT_CORE_PLANNER_TIMEOUT_SECONDS",
            default=30.0,
        ),
    )


def _read_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise PlannerModelConfigError(f"{name} must be an integer") from exc
    if value <= 0:
        raise PlannerModelConfigError(f"{name} must be greater than zero")
    return value


def _read_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise PlannerModelConfigError(f"{name} must be a number") from exc
    if value <= 0:
        raise PlannerModelConfigError(f"{name} must be greater than zero")
    return value
