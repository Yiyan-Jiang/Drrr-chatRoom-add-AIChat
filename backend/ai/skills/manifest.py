from dataclasses import dataclass, field

from ai.skills.errors import SkillContractError


_POLICY_KEYS = {"allow", "ask", "deny"}


@dataclass(frozen=True)
class SkillManifest:
    name: str
    version: int
    description: str
    instruction: str
    tools: list[str] = field(default_factory=list)
    artifact_contracts: dict[str, dict] = field(default_factory=dict)
    checkpoint_schema: dict = field(default_factory=dict)
    policy: dict = field(default_factory=dict)

    def validate(self, tool_registry) -> None:
        if not self.name.strip():
            raise SkillContractError("skill name is required")
        if self.version < 1:
            raise SkillContractError("skill version must be positive")
        if not self.instruction.strip():
            raise SkillContractError("skill instruction is required")

        known_tools = set(tool_registry.list_names())
        for tool_name in self.tools:
            if tool_name not in known_tools:
                raise SkillContractError(f"unknown tool: {tool_name}")

        if not isinstance(self.artifact_contracts, dict):
            raise SkillContractError("artifact_contracts must be an object")
        for artifact_type, contract in self.artifact_contracts.items():
            if not isinstance(artifact_type, str) or not artifact_type.strip():
                raise SkillContractError("artifact contract type is required")
            if not isinstance(contract, dict):
                raise SkillContractError("artifact contract must be an object")

        if not isinstance(self.checkpoint_schema, dict):
            raise SkillContractError("checkpoint_schema must be an object")

        if not isinstance(self.policy, dict):
            raise SkillContractError("policy must be an object")
        for key, values in self.policy.items():
            if key not in _POLICY_KEYS:
                raise SkillContractError(f"unknown policy key: {key}")
            if not isinstance(values, list):
                raise SkillContractError(f"policy {key} must be a list")
            for tool_name in values:
                if tool_name not in known_tools:
                    raise SkillContractError(f"unknown policy tool: {tool_name}")

    def summary(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": list(self.tools),
        }

    def to_state_entry(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "instruction": self.instruction,
            "tools": list(self.tools),
            "artifact_contracts": dict(self.artifact_contracts),
            "checkpoint_schema": dict(self.checkpoint_schema),
            "policy": dict(self.policy),
        }
