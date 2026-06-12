"""create agent platform state

Revision ID: 0002_create_agent_platform_state
Revises: 0001_create_ai_chat_history
Create Date: 2026-05-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_create_agent_platform_state"
down_revision: Union[str, None] = "0001_create_ai_chat_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("last_sequence_no", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extra_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("session_id", name="uq_agent_sessions_session_id"),
    )
    op.create_index("ix_agent_sessions_session_id", "agent_sessions", ["session_id"])
    op.create_index("ix_agent_sessions_user_id", "agent_sessions", ["user_id"])
    op.create_index("ix_agent_sessions_status", "agent_sessions", ["status"])
    op.create_index("ix_agent_sessions_user_updated", "agent_sessions", ["user_id", "updated_at"])

    op.create_table(
        "agent_turn_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("stage", sa.String(length=40), nullable=False, server_default="reserved"),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("debug_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("request_id", name="uq_agent_turn_audit_request_id"),
    )
    op.create_index("ix_agent_turn_audit_request_id", "agent_turn_audit", ["request_id"])
    op.create_index("ix_agent_turn_audit_user_id", "agent_turn_audit", ["user_id"])
    op.create_index("ix_agent_turn_audit_session_id", "agent_turn_audit", ["session_id"])
    op.create_index("ix_agent_turn_audit_status", "agent_turn_audit", ["status"])

    op.create_table(
        "agent_turns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("request_id", sa.String(length=80), nullable=True),
        sa.Column("character", sa.String(length=20), nullable=True),
        sa.Column("extra_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("session_id", "sequence_no", name="uq_agent_turns_session_sequence"),
    )
    op.create_index("ix_agent_turns_session_id", "agent_turns", ["session_id"])
    op.create_index("ix_agent_turns_user_id", "agent_turns", ["user_id"])
    op.create_index("ix_agent_turns_request_id", "agent_turns", ["request_id"])
    op.create_index("ix_agent_turns_session_sequence", "agent_turns", ["session_id", "sequence_no"])

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=80), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("aggregate_type", sa.String(length=40), nullable=False),
        sa.Column("aggregate_id", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=False),
        sa.Column("locked_at", sa.DateTime(), nullable=True),
        sa.Column("locked_by", sa.String(length=80), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("event_id", name="uq_outbox_events_event_id"),
    )
    op.create_index("ix_outbox_events_event_id", "outbox_events", ["event_id"])
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"])
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])
    op.create_index("ix_outbox_events_status", "outbox_events", ["status"])
    op.create_index("ix_outbox_events_next_attempt_at", "outbox_events", ["next_attempt_at"])
    op.create_index("ix_outbox_events_claim", "outbox_events", ["status", "next_attempt_at", "created_at"])

    op.create_table(
        "harness_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(length=80), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("request_id", sa.String(length=80), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="created"),
        sa.Column("checkpoint_payload", sa.JSON(), nullable=True),
        sa.Column("skill_state_payload", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("run_id", name="uq_harness_runs_run_id"),
    )
    op.create_index("ix_harness_runs_run_id", "harness_runs", ["run_id"])
    op.create_index("ix_harness_runs_session_id", "harness_runs", ["session_id"])
    op.create_index("ix_harness_runs_request_id", "harness_runs", ["request_id"])
    op.create_index("ix_harness_runs_user_id", "harness_runs", ["user_id"])
    op.create_index("ix_harness_runs_status", "harness_runs", ["status"])

    op.create_table(
        "harness_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(length=80), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_id", "sequence_no", name="uq_harness_events_run_sequence"),
    )
    op.create_index("ix_harness_events_run_id", "harness_events", ["run_id"])
    op.create_index("ix_harness_events_event_type", "harness_events", ["event_type"])

    op.create_table(
        "agent_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artifact_id", sa.String(length=80), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("run_id", sa.String(length=80), nullable=True),
        sa.Column("request_id", sa.String(length=80), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("artifact_id", name="uq_agent_artifacts_artifact_id"),
    )
    op.create_index("ix_agent_artifacts_artifact_id", "agent_artifacts", ["artifact_id"])
    op.create_index("ix_agent_artifacts_session_id", "agent_artifacts", ["session_id"])
    op.create_index("ix_agent_artifacts_run_id", "agent_artifacts", ["run_id"])
    op.create_index("ix_agent_artifacts_request_id", "agent_artifacts", ["request_id"])
    op.create_index("ix_agent_artifacts_user_id", "agent_artifacts", ["user_id"])
    op.create_index("ix_agent_artifacts_artifact_type", "agent_artifacts", ["artifact_type"])


def downgrade() -> None:
    op.drop_index("ix_agent_artifacts_artifact_type", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_user_id", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_request_id", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_run_id", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_session_id", table_name="agent_artifacts")
    op.drop_index("ix_agent_artifacts_artifact_id", table_name="agent_artifacts")
    op.drop_table("agent_artifacts")

    op.drop_index("ix_harness_events_event_type", table_name="harness_events")
    op.drop_index("ix_harness_events_run_id", table_name="harness_events")
    op.drop_table("harness_events")

    op.drop_index("ix_harness_runs_status", table_name="harness_runs")
    op.drop_index("ix_harness_runs_user_id", table_name="harness_runs")
    op.drop_index("ix_harness_runs_request_id", table_name="harness_runs")
    op.drop_index("ix_harness_runs_session_id", table_name="harness_runs")
    op.drop_index("ix_harness_runs_run_id", table_name="harness_runs")
    op.drop_table("harness_runs")

    op.drop_index("ix_outbox_events_claim", table_name="outbox_events")
    op.drop_index("ix_outbox_events_next_attempt_at", table_name="outbox_events")
    op.drop_index("ix_outbox_events_status", table_name="outbox_events")
    op.drop_index("ix_outbox_events_aggregate_id", table_name="outbox_events")
    op.drop_index("ix_outbox_events_event_type", table_name="outbox_events")
    op.drop_index("ix_outbox_events_event_id", table_name="outbox_events")
    op.drop_table("outbox_events")

    op.drop_index("ix_agent_turns_session_sequence", table_name="agent_turns")
    op.drop_index("ix_agent_turns_request_id", table_name="agent_turns")
    op.drop_index("ix_agent_turns_user_id", table_name="agent_turns")
    op.drop_index("ix_agent_turns_session_id", table_name="agent_turns")
    op.drop_table("agent_turns")

    op.drop_index("ix_agent_turn_audit_status", table_name="agent_turn_audit")
    op.drop_index("ix_agent_turn_audit_session_id", table_name="agent_turn_audit")
    op.drop_index("ix_agent_turn_audit_user_id", table_name="agent_turn_audit")
    op.drop_index("ix_agent_turn_audit_request_id", table_name="agent_turn_audit")
    op.drop_table("agent_turn_audit")

    op.drop_index("ix_agent_sessions_user_updated", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_status", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_user_id", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_session_id", table_name="agent_sessions")
    op.drop_table("agent_sessions")
