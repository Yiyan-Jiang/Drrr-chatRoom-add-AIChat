from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext, ToolPermission, ToolSpec
from ai.skills.errors import SkillError
from ai.skills.state import merge_manifest_into_state
from ai.skills.static_registry import create_default_skill_registry


def _require_mapping(arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    return dict(arguments)


def _normalize_open_skill(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    skill_name = normalized.get("skill_name")
    if not isinstance(skill_name, str) or not skill_name.strip():
        raise ValueError("skill_name is required")
    result = {"skill_name": skill_name.strip()}
    version = normalized.get("version")
    if version is not None:
        result["version"] = int(version)
    return result


async def _list_skills(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    registry = create_default_skill_registry(context.tool_registry)
    skills = registry.list_skills(user_id=context.user_id, workspace_id=context.workspace_id)
    if context.repository is not None and context.run is not None:
        await context.repository.append_event(
            context.run.run_id,
            "skills_listed",
            {"skills": skills},
        )
    return ToolResult(
        tool_name="list_skills",
        call_id=context.call_id,
        ok=True,
        result_kind="skills",
        preview=", ".join(skill["name"] for skill in skills),
        payload={"skills": skills},
    )


async def _open_skill(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    if context.repository is None or context.run is None:
        raise RuntimeError("skill state repository is not available")

    skill_name = arguments["skill_name"]
    version = arguments.get("version")
    await context.repository.append_event(
        context.run.run_id,
        "skill_open_requested",
        {"skill_name": skill_name, "version": version},
    )

    registry = create_default_skill_registry(context.tool_registry)
    try:
        manifest = registry.open_skill(
            skill_name,
            user_id=context.user_id,
            workspace_id=context.workspace_id,
            version=version,
        )
    except SkillError as exc:
        await context.repository.append_event(
            context.run.run_id,
            "skill_contract_rejected",
            {"skill_name": skill_name, "reason": str(exc)},
        )
        raise

    skill_state = merge_manifest_into_state(
        getattr(context.run, "skill_state_payload", None),
        manifest,
    )
    await context.repository.update_skill_state(context.run, skill_state)
    await context.repository.append_event(
        context.run.run_id,
        "skill_opened",
        {
            "name": manifest.name,
            "version": manifest.version,
            "tools": list(manifest.tools),
            "artifact_contracts": list(manifest.artifact_contracts.keys()),
        },
    )
    await context.repository.append_event(
        context.run.run_id,
        "skill_policy_merged",
        {"effective_policy": skill_state["effective_policy"]},
    )

    return ToolResult(
        tool_name="open_skill",
        call_id=context.call_id,
        ok=True,
        result_kind="skill_state",
        preview=f"opened {manifest.name}@{manifest.version}",
        payload={"skill_state": skill_state},
    )


def register_skill_tools(registry) -> None:
    registry.register(
        ToolSpec(
            name="list_skills",
            description="List runtime skills available to the current run.",
            input_schema={"type": "object", "properties": {}},
            permission=ToolPermission(scope="skills"),
            normalize=_require_mapping,
            execute=_list_skills,
        )
    )
    registry.register(
        ToolSpec(
            name="open_skill",
            description="Open a runtime skill and merge its state into the current run.",
            input_schema={
                "type": "object",
                "required": ["skill_name"],
                "properties": {
                    "skill_name": {"type": "string"},
                    "version": {"type": "integer"},
                },
            },
            permission=ToolPermission(scope="skills"),
            normalize=_normalize_open_skill,
            execute=_open_skill,
        )
    )
