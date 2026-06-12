from dataclasses import dataclass, field


@dataclass(frozen=True)
class PolicyLayer:
    policy_id: str
    version: int
    layer: str
    allowed_tools: set[str] = field(default_factory=set)
    ask_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class PolicyDecisionTrace:
    key: str
    value: str
    source_layer: str
    source_policy_id: str
    source_version: int
    reason: str

    def to_dict(self) -> dict[str, int | str]:
        return {
            "key": self.key,
            "value": self.value,
            "source_layer": self.source_layer,
            "source_policy_id": self.source_policy_id,
            "source_version": self.source_version,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class EffectivePolicy:
    tools: dict[str, str]
    trace: dict[str, PolicyDecisionTrace]

    def tool_decision(self, tool_name: str) -> str:
        return self.tools.get(tool_name, "deny")

    def trace_for(self, key: str) -> dict[str, int | str]:
        return self.trace[key].to_dict()

    def redacted(self) -> dict[str, dict[str, str]]:
        return {"tools": dict(sorted(self.tools.items()))}


def _trace(layer: PolicyLayer, tool_name: str, value: str) -> PolicyDecisionTrace:
    return PolicyDecisionTrace(
        key=f"tool.{tool_name}",
        value=value,
        source_layer=layer.layer,
        source_policy_id=layer.policy_id,
        source_version=layer.version,
        reason=f"{layer.layer} policy {value}s {tool_name}",
    )


def build_effective_policy(*layers: PolicyLayer | None) -> EffectivePolicy:
    tools: dict[str, str] = {}
    trace: dict[str, PolicyDecisionTrace] = {}

    for layer in [item for item in layers if item is not None]:
        for tool_name in sorted(layer.denied_tools):
            tools[tool_name] = "deny"
            trace[f"tool.{tool_name}"] = _trace(layer, tool_name, "deny")

        for tool_name in sorted(layer.ask_tools):
            if tools.get(tool_name) != "deny":
                tools[tool_name] = "ask"
                trace[f"tool.{tool_name}"] = _trace(layer, tool_name, "ask")

        for tool_name in sorted(layer.allowed_tools):
            if tools.get(tool_name) not in {"deny", "ask"}:
                tools[tool_name] = "allow"
                trace[f"tool.{tool_name}"] = _trace(layer, tool_name, "allow")

    return EffectivePolicy(tools=tools, trace=trace)
