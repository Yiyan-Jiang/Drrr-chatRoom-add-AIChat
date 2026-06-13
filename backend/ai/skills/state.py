from datetime import datetime

from ai.skills.manifest import SkillManifest


def empty_skill_state() -> dict:
    return {
        "opened_skills": [],
        "effective_tools": [],
        "effective_artifacts": [],
        "effective_policy": {"allow": [], "ask": [], "deny": []},
        "effective_checkpoint_schema": {},
    }


def merge_manifest_into_state(
    current_state: dict | None,
    manifest: SkillManifest,
    *,
    opened_at: datetime | None = None,
) -> dict:
    state = empty_skill_state()
    if current_state:
        state.update(current_state)

    opened_skills = list(state.get("opened_skills") or [])
    opened_skills = [
        item
        for item in opened_skills
        if not (item.get("name") == manifest.name and item.get("version") == manifest.version)
    ]
    entry = manifest.to_state_entry()
    entry["opened_at"] = (opened_at or datetime.now()).isoformat()
    opened_skills.append(entry)

    effective_tools = set(state.get("effective_tools") or [])
    effective_tools.update(manifest.tools)

    effective_artifacts = set(state.get("effective_artifacts") or [])
    effective_artifacts.update(manifest.artifact_contracts.keys())

    effective_policy = {
        "allow": list((state.get("effective_policy") or {}).get("allow") or []),
        "ask": list((state.get("effective_policy") or {}).get("ask") or []),
        "deny": list((state.get("effective_policy") or {}).get("deny") or []),
    }
    for key in ("allow", "ask", "deny"):
        merged_values = set(effective_policy[key])
        merged_values.update(manifest.policy.get(key, []))
        effective_policy[key] = sorted(merged_values)

    return {
        "opened_skills": opened_skills,
        "effective_tools": sorted(effective_tools),
        "effective_artifacts": sorted(effective_artifacts),
        "effective_policy": effective_policy,
        "effective_checkpoint_schema": dict(manifest.checkpoint_schema),
    }
