from dataclasses import dataclass
import json
from typing import Any

from ai.harness.planner_schema import LLM_PLANNER_ALLOWED_ACTIONS
from ai.prompts.character_service import normalize_character


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


DEFAULT_CONTEXT_TOKEN_BUDGET = 24000

# 段名 -> 优先级。数值越小越优先保留。必留段（优先级 0）即使超预算也不丢弃，
# 否则 planner 无法工作；历史类段优先级最高，超预算时最先被丢弃。
_SECTION_PRIORITY = {
    "current_input": 0,
    "run_policy": 0,
    "tool_schemas": 0,
    "workspace": 1,
    "checkpoint": 1,
    "skill_instructions": 1,
    "skill_state": 1,
    "skill_artifact_contracts": 1,
    "skill_checkpoint_schema": 1,
    "artifact_summaries": 2,
    "observations": 3,
    "recent_events": 4,
    "recent_turns": 5,
}
_DEFAULT_PRIORITY = 3


def _estimate_tokens(value: str) -> int:
    cjk = 0
    other = 0
    for ch in value:
        if "一" <= ch <= "鿿" or "　" <= ch <= "〿" or "＀" <= ch <= "￯":
            cjk += 1
        else:
            other += 1
    # CJK 字符约 0.6 token/字，其余约 4 char/token。
    return max(1, round(cjk * 0.6 + other / 4))


@dataclass(frozen=True)
class _SectionCandidate:
    section: str
    content: str
    role: str
    token_estimate: int


def _add_section(
    candidates: list[_SectionCandidate],
    section: str,
    content: str,
    role: str = "system",
) -> None:
    candidates.append(
        _SectionCandidate(
            section=section,
            content=content,
            role=role,
            token_estimate=_estimate_tokens(content) if content else 0,
        )
    )


def _select_within_budget(
    candidates: list[_SectionCandidate],
    token_budget: int,
) -> tuple[list[dict[str, str]], list[ContextLedgerItem]]:
    # 必留段（优先级 0）先占用预算，再按优先级从低到高纳入其余非空段。
    spent = sum(
        c.token_estimate
        for c in candidates
        if c.content and _SECTION_PRIORITY.get(c.section, _DEFAULT_PRIORITY) == 0
    )
    droppable = sorted(
        (c for c in candidates if c.content and _SECTION_PRIORITY.get(c.section, _DEFAULT_PRIORITY) != 0),
        key=lambda c: _SECTION_PRIORITY.get(c.section, _DEFAULT_PRIORITY),
    )
    kept_sections: set[str] = set()
    for candidate in droppable:
        if spent + candidate.token_estimate <= token_budget:
            spent += candidate.token_estimate
            kept_sections.add(candidate.section)

    messages: list[dict[str, str]] = []
    ledger: list[ContextLedgerItem] = []
    for candidate in candidates:
        if not candidate.content:
            ledger.append(
                ContextLedgerItem(
                    section=candidate.section,
                    included=False,
                    reason="empty",
                    token_estimate=0,
                )
            )
            continue
        priority = _SECTION_PRIORITY.get(candidate.section, _DEFAULT_PRIORITY)
        included = priority == 0 or candidate.section in kept_sections
        if included:
            messages.append({"role": candidate.role, "content": candidate.content})
        ledger.append(
            ContextLedgerItem(
                section=candidate.section,
                included=included,
                reason="included" if included else "budget",
                token_estimate=candidate.token_estimate,
            )
        )
    return messages, ledger


def compile_context(
    workspace,
    run,
    events: list,
    artifacts: list,
    registry=None,
    policy=None,
    token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
) -> CompiledContext:
    candidates: list[_SectionCandidate] = []

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

    _add_section(candidates, "workspace", f"session={workspace.session.session_id}")
    _add_section(candidates, "run_policy", _run_policy_content(policy))
    _add_section(candidates, "tool_schemas", _tool_schema_content(registry, policy))
    _add_section(candidates, "checkpoint", str(checkpoint or {}))
    _add_section(candidates, "skill_instructions", skill_instructions)
    _add_section(candidates, "skill_state", str(skill_state or {}))
    _add_section(candidates, "skill_artifact_contracts", str(artifact_contracts or {}))
    _add_section(candidates, "skill_checkpoint_schema", str(checkpoint_schemas or {}))
    _add_section(candidates, "recent_events", _recent_events_content(events))
    _add_section(candidates, "observations", _observations_content(events))
    _add_section(candidates, "artifact_summaries", _artifact_summaries_content(artifacts))
    _add_section(candidates, "recent_turns", _recent_turns_content(workspace.recent_turns))
    _add_section(candidates, "current_input", current_message, role="user")

    messages, ledger = _select_within_budget(candidates, token_budget)
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
