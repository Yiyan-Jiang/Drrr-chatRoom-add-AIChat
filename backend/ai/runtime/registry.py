from ai.runtime.tools import ToolSpec


class UnknownTool(Exception):
    pass


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"duplicate tool: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise UnknownTool(name) from exc

    def list_names(self) -> list[str]:
        return sorted(self._tools)

    def planner_tool_schemas(self, policy) -> list[dict]:
        allowed_tools = set(policy.allowed_tools)
        denied_tools = set(policy.denied_tools or [])
        schemas = []

        for name in sorted(self._tools):
            if name not in allowed_tools or name in denied_tools:
                continue
            spec = self._tools[name]
            schemas.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "when_to_use": spec.when_to_use,
                    "arguments_schema": spec.input_schema,
                    "permission": {
                        "scope": spec.permission.scope,
                        "requires_user_approval": spec.permission.requires_user_approval,
                    },
                }
            )

        return schemas
