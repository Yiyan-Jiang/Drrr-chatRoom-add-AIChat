from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, UniqueConstraint

from ai.database import AIBase


class AgentPolicyVersion(AIBase):
    __tablename__ = "agent_policy_versions"
    __table_args__ = (UniqueConstraint("policy_id", "version", name="uq_agent_policy_versions_policy_version"),)

    id: int = Column(Integer, primary_key=True)
    policy_id: str = Column(String(80), nullable=False, index=True)
    version: int = Column(Integer, nullable=False)
    layer: str = Column(String(30), nullable=False, index=True)
    payload: dict = Column(JSON, nullable=False)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_by: int | None = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AgentSkill(AIBase):
    __tablename__ = "agent_skills"

    id: int = Column(Integer, primary_key=True)
    skill_name: str = Column(String(120), nullable=False, unique=True, index=True)
    description: str | None = Column(Text, nullable=True)
    owner_id: int | None = Column(Integer, nullable=True, index=True)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AgentSkillVersion(AIBase):
    __tablename__ = "agent_skill_versions"
    __table_args__ = (UniqueConstraint("skill_name", "version", name="uq_agent_skill_versions_skill_version"),)

    id: int = Column(Integer, primary_key=True)
    skill_name: str = Column(String(120), nullable=False, index=True)
    version: int = Column(Integer, nullable=False)
    instruction: str = Column(Text, nullable=False)
    contract_payload: dict = Column(JSON, nullable=False)
    policy_payload: dict | None = Column(JSON, nullable=True)
    status: str = Column(String(30), nullable=False, default="draft", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AgentSkillRelease(AIBase):
    __tablename__ = "agent_skill_releases"

    id: int = Column(Integer, primary_key=True)
    release_id: str = Column(String(80), nullable=False, unique=True, index=True)
    skill_name: str = Column(String(120), nullable=False, index=True)
    version: int = Column(Integer, nullable=False)
    scope: str = Column(String(30), nullable=False, index=True)
    user_id: int | None = Column(Integer, nullable=True, index=True)
    workspace_id: str | None = Column(String(80), nullable=True, index=True)
    percentage: int = Column(Integer, nullable=False, default=0)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AgentSkillAuditLog(AIBase):
    __tablename__ = "agent_skill_audit_logs"

    id: int = Column(Integer, primary_key=True)
    audit_id: str = Column(String(80), nullable=False, unique=True, index=True)
    skill_name: str = Column(String(120), nullable=False, index=True)
    action: str = Column(String(80), nullable=False, index=True)
    operator_id: int | None = Column(Integer, nullable=True, index=True)
    payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class ModelRouteSet(AIBase):
    __tablename__ = "model_route_sets"

    id: int = Column(Integer, primary_key=True)
    route_set_id: str = Column(String(80), nullable=False, unique=True, index=True)
    name: str = Column(String(120), nullable=False)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_by: int | None = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class ModelRouteRule(AIBase):
    __tablename__ = "model_route_rules"

    id: int = Column(Integer, primary_key=True)
    rule_id: str = Column(String(80), nullable=False, unique=True, index=True)
    route_set_id: str = Column(String(80), nullable=False, index=True)
    task_type: str = Column(String(80), nullable=False, index=True)
    character: str | None = Column(String(80), nullable=True, index=True)
    provider: str = Column(String(80), nullable=False, index=True)
    model: str = Column(String(120), nullable=False)
    policy_tag: str | None = Column(String(80), nullable=True, index=True)
    cost_rank: int = Column(Integer, nullable=False, default=100)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class ModelRouteRelease(AIBase):
    __tablename__ = "model_route_releases"

    id: int = Column(Integer, primary_key=True)
    release_id: str = Column(String(80), nullable=False, unique=True, index=True)
    route_set_id: str = Column(String(80), nullable=False, index=True)
    scope: str = Column(String(30), nullable=False, index=True)
    user_id: int | None = Column(Integer, nullable=True, index=True)
    workspace_id: str | None = Column(String(80), nullable=True, index=True)
    percentage: int = Column(Integer, nullable=False, default=0)
    status: str = Column(String(30), nullable=False, default="active", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class ModelRouteAuditLog(AIBase):
    __tablename__ = "model_route_audit_logs"

    id: int = Column(Integer, primary_key=True)
    audit_id: str = Column(String(80), nullable=False, unique=True, index=True)
    route_set_id: str = Column(String(80), nullable=False, index=True)
    action: str = Column(String(80), nullable=False, index=True)
    operator_id: int | None = Column(Integer, nullable=True, index=True)
    payload: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class ProviderHealthSnapshot(AIBase):
    __tablename__ = "provider_health_snapshots"

    id: int = Column(Integer, primary_key=True)
    snapshot_id: str = Column(String(80), nullable=False, unique=True, index=True)
    provider: str = Column(String(80), nullable=False, index=True)
    metrics_payload: dict = Column(JSON, nullable=False)
    status: str = Column(String(30), nullable=False, default="healthy", index=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False, index=True)


class AdminChangeRequest(AIBase):
    __tablename__ = "admin_change_requests"

    id: int = Column(Integer, primary_key=True)
    change_id: str = Column(String(80), nullable=False, unique=True, index=True)
    target_type: str = Column(String(80), nullable=False, index=True)
    target_id: str = Column(String(120), nullable=False, index=True)
    patch_payload: dict = Column(JSON, nullable=False)
    status: str = Column(String(30), nullable=False, default="draft", index=True)
    requested_by: int | None = Column(Integer, nullable=True, index=True)
    applied_version: int | None = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AdminChangeApproval(AIBase):
    __tablename__ = "admin_change_approvals"

    id: int = Column(Integer, primary_key=True)
    approval_id: str = Column(String(80), nullable=False, unique=True, index=True)
    change_id: str = Column(String(80), nullable=False, index=True)
    operator_id: int = Column(Integer, nullable=False, index=True)
    decision: str = Column(String(30), nullable=False, index=True)
    comment: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)


class AdminAuditLog(AIBase):
    __tablename__ = "admin_audit_logs"

    id: int = Column(Integer, primary_key=True)
    audit_id: str = Column(String(80), nullable=False, unique=True, index=True)
    operator_id: int | None = Column(Integer, nullable=True, index=True)
    action: str = Column(String(80), nullable=False, index=True)
    target_type: str = Column(String(80), nullable=False, index=True)
    target_id: str = Column(String(120), nullable=False, index=True)
    before_payload: dict | None = Column(JSON, nullable=True)
    after_payload: dict | None = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.now, nullable=False)
