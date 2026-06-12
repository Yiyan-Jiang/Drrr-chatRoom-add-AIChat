from datetime import datetime
from typing import Any

from ai.models.governance_state import (
    AdminChangeRequest,
    AgentPolicyVersion,
    AgentSkillRelease,
    AgentSkillVersion,
)


async def create_policy_version(
    db,
    *,
    policy_id: str,
    version: int,
    layer: str,
    payload: dict[str, Any],
    created_by: int | None = None,
    now: datetime | None = None,
) -> AgentPolicyVersion:
    timestamp = now or datetime.now()
    record = AgentPolicyVersion(
        policy_id=policy_id,
        version=version,
        layer=layer,
        payload=payload,
        status="active",
        created_by=created_by,
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.add(record)
    await db.flush()
    return record


async def create_skill_version(
    db,
    *,
    skill_name: str,
    version: int,
    instruction: str,
    tools: list[str],
    artifact_contracts: list[str],
    policy_payload: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> AgentSkillVersion:
    timestamp = now or datetime.now()
    record = AgentSkillVersion(
        skill_name=skill_name,
        version=version,
        instruction=instruction,
        contract_payload={
            "tools": tools,
            "artifact_contracts": artifact_contracts,
        },
        policy_payload=policy_payload,
        status="draft",
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.add(record)
    await db.flush()
    return record


async def create_skill_release(
    db,
    *,
    release_id: str,
    skill_name: str,
    version: int,
    scope: str,
    percentage: int,
    user_id: int | None = None,
    workspace_id: str | None = None,
    now: datetime | None = None,
) -> AgentSkillRelease:
    timestamp = now or datetime.now()
    record = AgentSkillRelease(
        release_id=release_id,
        skill_name=skill_name,
        version=version,
        scope=scope,
        user_id=user_id,
        workspace_id=workspace_id,
        percentage=percentage,
        status="active",
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.add(record)
    await db.flush()
    return record


async def create_admin_change_request(
    db,
    *,
    change_id: str,
    target_type: str,
    target_id: str,
    patch: dict[str, Any],
    requested_by: int | None = None,
    now: datetime | None = None,
) -> AdminChangeRequest:
    timestamp = now or datetime.now()
    record = AdminChangeRequest(
        change_id=change_id,
        target_type=target_type,
        target_id=target_id,
        patch_payload=patch,
        status="draft",
        requested_by=requested_by,
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.add(record)
    await db.flush()
    return record
