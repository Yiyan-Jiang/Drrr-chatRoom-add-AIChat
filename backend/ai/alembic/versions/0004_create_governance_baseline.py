"""create governance baseline

Revision ID: 0004_create_governance_baseline
Revises: 0003_create_knowledge_baseline
Create Date: 2026-05-26 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_create_governance_baseline"
down_revision: Union[str, None] = "0003_create_knowledge_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_policy_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("policy_id", sa.String(length=80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("layer", sa.String(length=30), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("policy_id", "version", name="uq_agent_policy_versions_policy_version"),
    )
    op.create_index("ix_agent_policy_versions_policy_id", "agent_policy_versions", ["policy_id"])
    op.create_index("ix_agent_policy_versions_layer", "agent_policy_versions", ["layer"])
    op.create_index("ix_agent_policy_versions_status", "agent_policy_versions", ["status"])

    op.create_table(
        "agent_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("skill_name", name="uq_agent_skills_skill_name"),
    )
    op.create_index("ix_agent_skills_skill_name", "agent_skills", ["skill_name"])
    op.create_index("ix_agent_skills_owner_id", "agent_skills", ["owner_id"])
    op.create_index("ix_agent_skills_status", "agent_skills", ["status"])

    op.create_table(
        "agent_skill_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("contract_payload", sa.JSON(), nullable=False),
        sa.Column("policy_payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("skill_name", "version", name="uq_agent_skill_versions_skill_version"),
    )
    op.create_index("ix_agent_skill_versions_skill_name", "agent_skill_versions", ["skill_name"])
    op.create_index("ix_agent_skill_versions_status", "agent_skill_versions", ["status"])

    op.create_table(
        "agent_skill_releases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("release_id", sa.String(length=80), nullable=False),
        sa.Column("skill_name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("scope", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("workspace_id", sa.String(length=80), nullable=True),
        sa.Column("percentage", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("release_id", name="uq_agent_skill_releases_release_id"),
    )
    op.create_index("ix_agent_skill_releases_release_id", "agent_skill_releases", ["release_id"])
    op.create_index("ix_agent_skill_releases_skill_name", "agent_skill_releases", ["skill_name"])
    op.create_index("ix_agent_skill_releases_scope", "agent_skill_releases", ["scope"])
    op.create_index("ix_agent_skill_releases_user_id", "agent_skill_releases", ["user_id"])
    op.create_index("ix_agent_skill_releases_workspace_id", "agent_skill_releases", ["workspace_id"])
    op.create_index("ix_agent_skill_releases_status", "agent_skill_releases", ["status"])

    op.create_table(
        "agent_skill_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_id", sa.String(length=80), nullable=False),
        sa.Column("skill_name", sa.String(length=120), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("audit_id", name="uq_agent_skill_audit_logs_audit_id"),
    )
    op.create_index("ix_agent_skill_audit_logs_audit_id", "agent_skill_audit_logs", ["audit_id"])
    op.create_index("ix_agent_skill_audit_logs_skill_name", "agent_skill_audit_logs", ["skill_name"])
    op.create_index("ix_agent_skill_audit_logs_action", "agent_skill_audit_logs", ["action"])
    op.create_index("ix_agent_skill_audit_logs_operator_id", "agent_skill_audit_logs", ["operator_id"])

    op.create_table(
        "model_route_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("route_set_id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("route_set_id", name="uq_model_route_sets_route_set_id"),
    )
    op.create_index("ix_model_route_sets_route_set_id", "model_route_sets", ["route_set_id"])
    op.create_index("ix_model_route_sets_status", "model_route_sets", ["status"])

    op.create_table(
        "model_route_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.String(length=80), nullable=False),
        sa.Column("route_set_id", sa.String(length=80), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("character", sa.String(length=80), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("policy_tag", sa.String(length=80), nullable=True),
        sa.Column("cost_rank", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("rule_id", name="uq_model_route_rules_rule_id"),
    )
    op.create_index("ix_model_route_rules_rule_id", "model_route_rules", ["rule_id"])
    op.create_index("ix_model_route_rules_route_set_id", "model_route_rules", ["route_set_id"])
    op.create_index("ix_model_route_rules_task_type", "model_route_rules", ["task_type"])
    op.create_index("ix_model_route_rules_character", "model_route_rules", ["character"])
    op.create_index("ix_model_route_rules_provider", "model_route_rules", ["provider"])
    op.create_index("ix_model_route_rules_policy_tag", "model_route_rules", ["policy_tag"])
    op.create_index("ix_model_route_rules_status", "model_route_rules", ["status"])

    op.create_table(
        "model_route_releases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("release_id", sa.String(length=80), nullable=False),
        sa.Column("route_set_id", sa.String(length=80), nullable=False),
        sa.Column("scope", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("workspace_id", sa.String(length=80), nullable=True),
        sa.Column("percentage", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("release_id", name="uq_model_route_releases_release_id"),
    )
    op.create_index("ix_model_route_releases_release_id", "model_route_releases", ["release_id"])
    op.create_index("ix_model_route_releases_route_set_id", "model_route_releases", ["route_set_id"])
    op.create_index("ix_model_route_releases_scope", "model_route_releases", ["scope"])
    op.create_index("ix_model_route_releases_user_id", "model_route_releases", ["user_id"])
    op.create_index("ix_model_route_releases_workspace_id", "model_route_releases", ["workspace_id"])
    op.create_index("ix_model_route_releases_status", "model_route_releases", ["status"])

    op.create_table(
        "model_route_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_id", sa.String(length=80), nullable=False),
        sa.Column("route_set_id", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("audit_id", name="uq_model_route_audit_logs_audit_id"),
    )
    op.create_index("ix_model_route_audit_logs_audit_id", "model_route_audit_logs", ["audit_id"])
    op.create_index("ix_model_route_audit_logs_route_set_id", "model_route_audit_logs", ["route_set_id"])
    op.create_index("ix_model_route_audit_logs_action", "model_route_audit_logs", ["action"])
    op.create_index("ix_model_route_audit_logs_operator_id", "model_route_audit_logs", ["operator_id"])

    op.create_table(
        "provider_health_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("snapshot_id", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("metrics_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("snapshot_id", name="uq_provider_health_snapshots_snapshot_id"),
    )
    op.create_index("ix_provider_health_snapshots_snapshot_id", "provider_health_snapshots", ["snapshot_id"])
    op.create_index("ix_provider_health_snapshots_provider", "provider_health_snapshots", ["provider"])
    op.create_index("ix_provider_health_snapshots_status", "provider_health_snapshots", ["status"])
    op.create_index("ix_provider_health_snapshots_created_at", "provider_health_snapshots", ["created_at"])

    op.create_table(
        "admin_change_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("change_id", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=120), nullable=False),
        sa.Column("patch_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("applied_version", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("change_id", name="uq_admin_change_requests_change_id"),
    )
    op.create_index("ix_admin_change_requests_change_id", "admin_change_requests", ["change_id"])
    op.create_index("ix_admin_change_requests_target_type", "admin_change_requests", ["target_type"])
    op.create_index("ix_admin_change_requests_target_id", "admin_change_requests", ["target_id"])
    op.create_index("ix_admin_change_requests_status", "admin_change_requests", ["status"])
    op.create_index("ix_admin_change_requests_requested_by", "admin_change_requests", ["requested_by"])

    op.create_table(
        "admin_change_approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("approval_id", sa.String(length=80), nullable=False),
        sa.Column("change_id", sa.String(length=80), nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=30), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("approval_id", name="uq_admin_change_approvals_approval_id"),
    )
    op.create_index("ix_admin_change_approvals_approval_id", "admin_change_approvals", ["approval_id"])
    op.create_index("ix_admin_change_approvals_change_id", "admin_change_approvals", ["change_id"])
    op.create_index("ix_admin_change_approvals_operator_id", "admin_change_approvals", ["operator_id"])
    op.create_index("ix_admin_change_approvals_decision", "admin_change_approvals", ["decision"])

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_id", sa.String(length=80), nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=120), nullable=False),
        sa.Column("before_payload", sa.JSON(), nullable=True),
        sa.Column("after_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("audit_id", name="uq_admin_audit_logs_audit_id"),
    )
    op.create_index("ix_admin_audit_logs_audit_id", "admin_audit_logs", ["audit_id"])
    op.create_index("ix_admin_audit_logs_operator_id", "admin_audit_logs", ["operator_id"])
    op.create_index("ix_admin_audit_logs_action", "admin_audit_logs", ["action"])
    op.create_index("ix_admin_audit_logs_target_type", "admin_audit_logs", ["target_type"])
    op.create_index("ix_admin_audit_logs_target_id", "admin_audit_logs", ["target_id"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_logs_target_id", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_target_type", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_action", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_operator_id", table_name="admin_audit_logs")
    op.drop_index("ix_admin_audit_logs_audit_id", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")

    op.drop_index("ix_admin_change_approvals_decision", table_name="admin_change_approvals")
    op.drop_index("ix_admin_change_approvals_operator_id", table_name="admin_change_approvals")
    op.drop_index("ix_admin_change_approvals_change_id", table_name="admin_change_approvals")
    op.drop_index("ix_admin_change_approvals_approval_id", table_name="admin_change_approvals")
    op.drop_table("admin_change_approvals")

    op.drop_index("ix_admin_change_requests_requested_by", table_name="admin_change_requests")
    op.drop_index("ix_admin_change_requests_status", table_name="admin_change_requests")
    op.drop_index("ix_admin_change_requests_target_id", table_name="admin_change_requests")
    op.drop_index("ix_admin_change_requests_target_type", table_name="admin_change_requests")
    op.drop_index("ix_admin_change_requests_change_id", table_name="admin_change_requests")
    op.drop_table("admin_change_requests")

    op.drop_index("ix_provider_health_snapshots_created_at", table_name="provider_health_snapshots")
    op.drop_index("ix_provider_health_snapshots_status", table_name="provider_health_snapshots")
    op.drop_index("ix_provider_health_snapshots_provider", table_name="provider_health_snapshots")
    op.drop_index("ix_provider_health_snapshots_snapshot_id", table_name="provider_health_snapshots")
    op.drop_table("provider_health_snapshots")

    op.drop_index("ix_model_route_audit_logs_operator_id", table_name="model_route_audit_logs")
    op.drop_index("ix_model_route_audit_logs_action", table_name="model_route_audit_logs")
    op.drop_index("ix_model_route_audit_logs_route_set_id", table_name="model_route_audit_logs")
    op.drop_index("ix_model_route_audit_logs_audit_id", table_name="model_route_audit_logs")
    op.drop_table("model_route_audit_logs")

    op.drop_index("ix_model_route_releases_status", table_name="model_route_releases")
    op.drop_index("ix_model_route_releases_workspace_id", table_name="model_route_releases")
    op.drop_index("ix_model_route_releases_user_id", table_name="model_route_releases")
    op.drop_index("ix_model_route_releases_scope", table_name="model_route_releases")
    op.drop_index("ix_model_route_releases_route_set_id", table_name="model_route_releases")
    op.drop_index("ix_model_route_releases_release_id", table_name="model_route_releases")
    op.drop_table("model_route_releases")

    op.drop_index("ix_model_route_rules_status", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_policy_tag", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_provider", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_character", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_task_type", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_route_set_id", table_name="model_route_rules")
    op.drop_index("ix_model_route_rules_rule_id", table_name="model_route_rules")
    op.drop_table("model_route_rules")

    op.drop_index("ix_model_route_sets_status", table_name="model_route_sets")
    op.drop_index("ix_model_route_sets_route_set_id", table_name="model_route_sets")
    op.drop_table("model_route_sets")

    op.drop_index("ix_agent_skill_audit_logs_operator_id", table_name="agent_skill_audit_logs")
    op.drop_index("ix_agent_skill_audit_logs_action", table_name="agent_skill_audit_logs")
    op.drop_index("ix_agent_skill_audit_logs_skill_name", table_name="agent_skill_audit_logs")
    op.drop_index("ix_agent_skill_audit_logs_audit_id", table_name="agent_skill_audit_logs")
    op.drop_table("agent_skill_audit_logs")

    op.drop_index("ix_agent_skill_releases_status", table_name="agent_skill_releases")
    op.drop_index("ix_agent_skill_releases_workspace_id", table_name="agent_skill_releases")
    op.drop_index("ix_agent_skill_releases_user_id", table_name="agent_skill_releases")
    op.drop_index("ix_agent_skill_releases_scope", table_name="agent_skill_releases")
    op.drop_index("ix_agent_skill_releases_skill_name", table_name="agent_skill_releases")
    op.drop_index("ix_agent_skill_releases_release_id", table_name="agent_skill_releases")
    op.drop_table("agent_skill_releases")

    op.drop_index("ix_agent_skill_versions_status", table_name="agent_skill_versions")
    op.drop_index("ix_agent_skill_versions_skill_name", table_name="agent_skill_versions")
    op.drop_table("agent_skill_versions")

    op.drop_index("ix_agent_skills_status", table_name="agent_skills")
    op.drop_index("ix_agent_skills_owner_id", table_name="agent_skills")
    op.drop_index("ix_agent_skills_skill_name", table_name="agent_skills")
    op.drop_table("agent_skills")

    op.drop_index("ix_agent_policy_versions_status", table_name="agent_policy_versions")
    op.drop_index("ix_agent_policy_versions_layer", table_name="agent_policy_versions")
    op.drop_index("ix_agent_policy_versions_policy_id", table_name="agent_policy_versions")
    op.drop_table("agent_policy_versions")
