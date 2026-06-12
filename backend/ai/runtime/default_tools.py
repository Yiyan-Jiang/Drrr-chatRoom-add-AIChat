from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext, ToolPermission, ToolSpec
from ai.skills.tools import register_skill_tools
from ai.skills.teaching.tools import register_teaching_tools


def _require_mapping(arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    return dict(arguments)


async def _read_checkpoint(
    context: ToolExecutionContext,
    _arguments: dict,
) -> ToolResult:
    checkpoint = context.checkpoint_payload or {}
    return ToolResult(
        tool_name="read_checkpoint",
        call_id=context.call_id,
        ok=True,
        result_kind="checkpoint",
        preview=str(checkpoint),
        payload={"checkpoint": checkpoint},
    )


def _normalize_read_artifact(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    artifact_id = normalized.get("artifact_id")
    artifact_type = normalized.get("artifact_type")
    if artifact_id is not None and (
        not isinstance(artifact_id, str) or not artifact_id.strip()
    ):
        raise ValueError("artifact_id must be a non-empty string")
    if artifact_type is not None and (
        not isinstance(artifact_type, str) or not artifact_type.strip()
    ):
        raise ValueError("artifact_type must be a non-empty string")
    if not artifact_id and not artifact_type:
        raise ValueError("artifact_id or artifact_type is required")
    result = {}
    if artifact_id:
        result["artifact_id"] = artifact_id.strip()
    if artifact_type:
        result["artifact_type"] = artifact_type.strip()
    return result


async def _read_artifact(
    context: ToolExecutionContext,
    arguments: dict,
) -> ToolResult:
    if context.repository is None:
        raise RuntimeError("artifact repository is not available")

    artifacts = await context.repository.list_artifacts(context.run_id)
    artifact = _find_artifact(artifacts, arguments)
    if artifact is None:
        return ToolResult(
            tool_name="read_artifact",
            call_id=context.call_id,
            ok=False,
            result_kind="artifact",
            preview="artifact not found",
            payload={},
            error_code="ARTIFACT_NOT_FOUND",
            error_message="artifact not found",
        )

    payload = getattr(artifact, "payload", None) or {}
    preview = _artifact_preview(artifact)
    return ToolResult(
        tool_name="read_artifact",
        call_id=context.call_id,
        ok=True,
        result_kind="artifact",
        preview=preview,
        payload={
            "artifact": {
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "preview": preview,
                "payload": payload,
            }
        },
    )


def _normalize_write_artifact(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    artifact_type = normalized.get("artifact_type")
    payload = normalized.get("payload")
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        raise ValueError("artifact_type is required")
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    return {"artifact_type": artifact_type.strip(), "payload": payload}


async def _write_artifact(
    context: ToolExecutionContext,
    arguments: dict,
) -> ToolResult:
    if context.repository is None or context.run is None:
        raise RuntimeError("artifact repository is not available")
    _assert_artifact_allowed(context, arguments["artifact_type"])

    artifact = await context.repository.write_artifact(
        context.run,
        arguments["artifact_type"],
        arguments["payload"],
    )
    return ToolResult(
        tool_name="write_artifact",
        call_id=context.call_id,
        ok=True,
        result_kind="artifact",
        preview=arguments["artifact_type"],
        payload={"artifact_type": artifact.artifact_type},
    )


def _normalize_update_checkpoint(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    patch = normalized.get("patch")
    if not isinstance(patch, dict):
        raise ValueError("patch must be an object")
    return {"patch": dict(patch)}


async def _update_checkpoint(
    context: ToolExecutionContext,
    arguments: dict,
) -> ToolResult:
    if context.repository is None or context.run is None:
        raise RuntimeError("checkpoint repository is not available")

    current = dict(context.checkpoint_payload or {})
    current.update(arguments["patch"])
    run = await context.repository.update_checkpoint(context.run, current)
    checkpoint = getattr(run, "checkpoint_payload", current) or current
    return ToolResult(
        tool_name="update_checkpoint",
        call_id=context.call_id,
        ok=True,
        result_kind="checkpoint",
        preview=str(checkpoint),
        payload={"checkpoint": checkpoint},
    )


def _normalize_record_note(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    note = normalized.get("note")
    if not isinstance(note, str) or not note.strip():
        raise ValueError("note is required")
    return {"note": note.strip()}


async def _record_note(
    context: ToolExecutionContext,
    arguments: dict,
) -> ToolResult:
    if context.repository is None or context.run is None:
        raise RuntimeError("artifact repository is not available")
    _assert_artifact_allowed(context, "runtime_note")

    artifact = await context.repository.write_artifact(
        context.run,
        "runtime_note",
        {"note": arguments["note"]},
    )
    return ToolResult(
        tool_name="record_note",
        call_id=context.call_id,
        ok=True,
        result_kind="artifact",
        preview=arguments["note"],
        payload={"artifact_type": artifact.artifact_type},
    )


def _assert_artifact_allowed(context: ToolExecutionContext, artifact_type: str) -> None:
    skill_state = getattr(context.run, "skill_state_payload", None) if context.run else None
    effective_artifacts = set((skill_state or {}).get("effective_artifacts") or [])
    if effective_artifacts and artifact_type not in effective_artifacts:
        raise PermissionError(f"artifact type not allowed: {artifact_type}")


def _find_artifact(artifacts: list, arguments: dict):
    artifact_id = arguments.get("artifact_id")
    artifact_type = arguments.get("artifact_type")
    matches = []
    for artifact in artifacts:
        if artifact_id and getattr(artifact, "artifact_id", None) != artifact_id:
            continue
        if artifact_type and getattr(artifact, "artifact_type", None) != artifact_type:
            continue
        matches.append(artifact)
    return matches[-1] if matches else None


def _artifact_preview(artifact) -> str:
    payload = getattr(artifact, "payload", None) or {}
    summary = payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    return str(getattr(artifact, "artifact_type", "artifact"))


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="read_checkpoint",
            description="Read the current harness checkpoint.",
            input_schema={"type": "object", "properties": {}},
            permission=ToolPermission(scope="runtime_state"),
            normalize=_require_mapping,
            execute=_read_checkpoint,
        )
    )
    registry.register(
        ToolSpec(
            name="read_artifact",
            description="Read a structured runtime artifact by id or type.",
            input_schema={
                "type": "object",
                "properties": {
                    "artifact_id": {"type": "string"},
                    "artifact_type": {"type": "string"},
                },
            },
            permission=ToolPermission(scope="runtime_state"),
            normalize=_normalize_read_artifact,
            execute=_read_artifact,
            when_to_use="Use after an artifact was written and the planner needs its stored state.",
        )
    )
    registry.register(
        ToolSpec(
            name="write_artifact",
            description="Write a structured runtime artifact.",
            input_schema={
                "type": "object",
                "required": ["artifact_type", "payload"],
                "properties": {
                    "artifact_type": {"type": "string"},
                    "payload": {"type": "object"},
                },
            },
            permission=ToolPermission(scope="runtime_state"),
            normalize=_normalize_write_artifact,
            execute=_write_artifact,
        )
    )
    registry.register(
        ToolSpec(
            name="update_checkpoint",
            description="Merge a small JSON patch into the current harness checkpoint.",
            input_schema={
                "type": "object",
                "required": ["patch"],
                "properties": {"patch": {"type": "object"}},
            },
            permission=ToolPermission(scope="runtime_state"),
            normalize=_normalize_update_checkpoint,
            execute=_update_checkpoint,
            when_to_use="Use when the planner needs to persist short recoverable run state.",
        )
    )
    registry.register(
        ToolSpec(
            name="record_note",
            description="Record a structured runtime note artifact.",
            input_schema={
                "type": "object",
                "required": ["note"],
                "properties": {"note": {"type": "string"}},
            },
            permission=ToolPermission(scope="runtime_state"),
            normalize=_normalize_record_note,
            execute=_record_note,
        )
    )
    register_teaching_tools(registry)
    register_skill_tools(registry)
    return registry
