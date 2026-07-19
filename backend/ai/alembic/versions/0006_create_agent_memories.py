"""create agent memories

Revision ID: 0006_create_agent_memories
Revises: 0005_harness_skill_state
Create Date: 2026-07-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_create_agent_memories"
down_revision: Union[str, None] = "0005_harness_skill_state"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("memory_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("character", sa.String(length=20), nullable=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("source_turn_id", sa.Integer(), nullable=True),
        sa.Column("source_sequence_no", sa.Integer(), nullable=True),
        sa.Column("memory_type", sa.String(length=40), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("memory_id", name="uq_agent_memories_memory_id"),
    )
    op.create_index("ix_agent_memories_memory_id", "agent_memories", ["memory_id"])
    op.create_index("ix_agent_memories_user_id", "agent_memories", ["user_id"])
    op.create_index("ix_agent_memories_character", "agent_memories", ["character"])
    op.create_index("ix_agent_memories_session_id", "agent_memories", ["session_id"])
    op.create_index("ix_agent_memories_source_turn_id", "agent_memories", ["source_turn_id"])
    op.create_index("ix_agent_memories_memory_type", "agent_memories", ["memory_type"])
    op.create_index("ix_agent_memories_status", "agent_memories", ["status"])
    op.create_index(
        "ix_agent_memories_user_character_status",
        "agent_memories",
        ["user_id", "character", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_agent_memories_user_character_status", table_name="agent_memories")
    op.drop_index("ix_agent_memories_status", table_name="agent_memories")
    op.drop_index("ix_agent_memories_memory_type", table_name="agent_memories")
    op.drop_index("ix_agent_memories_source_turn_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_session_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_character", table_name="agent_memories")
    op.drop_index("ix_agent_memories_user_id", table_name="agent_memories")
    op.drop_index("ix_agent_memories_memory_id", table_name="agent_memories")
    op.drop_table("agent_memories")
