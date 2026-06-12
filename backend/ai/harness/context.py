from dataclasses import dataclass
import json
from typing import Any

from ai.harness.planner_schema import LLM_PLANNER_ALLOWED_ACTIONS
from ai.prompts.character_service import get_system_prompt, normalize_character


@dataclass(frozen=True)
class ContextLedgerItem:
    section: str
    included: bool
    reason: str
    token_estimate: int


@dataclass(frozen=True)
class CompiledContext:
    messages: list[dict[str, str]]
    ledger: list[ContextLedgerItem]
    token_estimate: int


def _estimate_tokens(value: str) -> int:
    return max(1, len(value) // 4)


def _add_section(
    messages: list[dict[str, str]],
    ledger: list[ContextLedgerItem],
    section: str,
    content: str,
    role: str = "system",
) -> None:
    included = bool(content)
    token_estimate = _estimate_tokens(content) if included else 0
    if included:
        messages.append({"role": role, "content": content})
    ledger.append(
        ContextLedgerItem(
            section=section,
            included=included,
            reason="included" if included else "empty",
            token_estimate=token_estimate,
        )
    )


def compile_context(
    workspace,
    run,
    events: list,
    artifacts: list,
    registry=None,
    policy=None,
) -> CompiledContext:
    messages: list[dict[str, str]] = []
    ledger: list[ContextLedgerItem] = []

    checkpoint = getattr(run, "checkpoint_payload", None)
    skill_state = getattr(run, "skill_state_payload", None) or {}
    opened_skills = skill_state.get("opened_skills") or []
    skill_instructions = "\n".join(
        skill.get("instruction", "") for skill in opened_skills if skill.get("instruction")
    )
    artifact_contracts = {
        skill.get("name"): skill.get("artifact_contracts", {})
        for skill in opened_skills
        if skill.get("artifact_contracts")
    }
    checkpoint_schemas = {
        skill.get("name"): skill.get("checkpoint_schema", {})
        for skill in opened_skills
        if skill.get("checkpoint_schema")
    }
    current_message = getattr(workspace.command, "message", "")
    character = normalize_character(getattr(workspace.command, "character", None))

    _add_section(messages, ledger, "workspace", f"session={workspace.session.session_id}")
    _add_section(messages, ledger, "character_prompt", get_system_prompt(character))
    _add_section(messages, ledger, "run_policy", _run_policy_content(policy))
    _add_section(messages, ledger, "tool_schemas", _tool_schema_content(registry, policy))
    _add_section(messages, ledger, "checkpoint", str(checkpoint or {}))
    _add_section(messages, ledger, "skill_instructions", skill_instructions)
    _add_section(messages, ledger, "skill_state", str(skill_state or {}))
    _add_section(messages, ledger, "skill_artifact_contracts", str(artifact_contracts or {}))
    _add_section(messages, ledger, "skill_checkpoint_schema", str(checkpoint_schemas or {}))
    _add_section(messages, ledger, "recent_events", _recent_events_content(events))
    _add_section(messages, ledger, "observations", _observations_content(events))
    _add_section(messages, ledger, "artifact_summaries", _artifact_summaries_content(artifacts))
    _add_section(messages, ledger, "recent_turns", _recent_turns_content(workspace.recent_turns))
    _add_section(messages, ledger, "current_input", current_message, role="user")

    return CompiledContext(
        messages=messages,
        ledger=ledger,
        token_estimate=sum(item.token_estimate for item in ledger if item.included),
    )


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _run_policy_content(policy) -> str:
    visible_tools = []
    if policy is not None:
        denied_tools = set(policy.denied_tools or [])
        visible_tools = [
            tool for tool in policy.allowed_tools if tool not in denied_tools
        ]
    return _json(
        {
            "allowed_actions": LLM_PLANNER_ALLOWED_ACTIONS,
            "allowed_tools": sorted(visible_tools),
            "state_rules": [
                "artifacts and checkpoint may only be read or changed through tools",
                "planner output must be one JSON object",
            ],
        }
    )


def _tool_schema_content(registry, policy) -> str:
    if registry is None or policy is None:
        return ""
    return _json(registry.planner_tool_schemas(policy))


def _recent_events_content(events: list) -> str:
    summaries = []
    for event in events[-10:]:
        summaries.append(
            {
                "event_type": getattr(event, "event_type", ""),
                "payload": _compact_payload(getattr(event, "payload", {}) or {}),
            }
        )
    return _json(summaries) if summaries else ""


def _observations_content(events: list) -> str:
    observations = []
    for event in events[-10:]:
        if getattr(event, "event_type", "") != "tool_result":
            continue
        payload = getattr(event, "payload", {}) or {}
        result = payload.get("result") or {}
        observations.append(
            {
                "call_id": payload.get("call_id"),
                "tool": payload.get("tool"),
                "ok": result.get("ok"),
                "result_kind": result.get("result_kind"),
                "preview": result.get("preview"),
                "error_code": result.get("error_code"),
            }
        )
    return _json(observations) if observations else ""


def _artifact_summaries_content(artifacts: list) -> str:
    summaries = []
    for artifact in artifacts:
        payload = getattr(artifact, "payload", None) or {}
        summary = payload.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            summary = str(getattr(artifact, "artifact_type", "artifact"))
        summaries.append(
            {
                "artifact_id": getattr(artifact, "artifact_id", None),
                "artifact_type": getattr(artifact, "artifact_type", None),
                "summary": summary,
            }
        )
    return _json(summaries) if summaries else ""


def _recent_turns_content(turns: list) -> str:
    summaries = []
    for turn in turns:
        content = getattr(turn, "content", "")
        if not isinstance(content, str):
            content = str(content)
        summaries.append(
            {
                "sequence_no": getattr(turn, "sequence_no", None),
                "role": getattr(turn, "role", ""),
                "character": getattr(turn, "character", None),
                "content": content[:2000],
            }
        )
    return _json(summaries) if summaries else ""


def _compact_payload(payload: dict) -> dict:
    compact = {}
    for key in ("call_id", "tool", "artifact_id", "artifact_type", "error_code"):
        if key in payload:
            compact[key] = payload[key]
    result = payload.get("result")
    if isinstance(result, dict):
        compact["result"] = {
            key: result.get(key)
            for key in ("ok", "result_kind", "preview", "error_code")
            if key in result
        }
    return compact or {"summary": str(payload)[:300]}
