from dataclasses import dataclass

from ai.governance.policy import PolicyLayer, build_effective_policy
from ai.governance.skills import SkillRegistry


@dataclass(frozen=True)
class PolicySimulationResult:
    decision: str
    effective_policy: dict
    trace: dict
    skill_version: int


def simulate_policy(
    *,
    policies: list[PolicyLayer],
    skill_registry: SkillRegistry,
    requested_skill: str,
    user_id: int,
    workspace_id: str | None,
    tool_name: str,
) -> PolicySimulationResult:
    skill = skill_registry.resolve_for_run(
        requested_skill,
        user_id=user_id,
        workspace_id=workspace_id,
    )
    effective = build_effective_policy(*policies)
    return PolicySimulationResult(
        decision=effective.tool_decision(tool_name),
        effective_policy=effective.redacted(),
        trace={key: value.to_dict() for key, value in effective.trace.items()},
        skill_version=skill.version,
    )
