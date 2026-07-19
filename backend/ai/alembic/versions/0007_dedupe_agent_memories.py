"""dedupe agent memories

Revision ID: 0007_dedupe_agent_memories
Revises: 0006_create_agent_memories
Create Date: 2026-07-19
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0007_dedupe_agent_memories"
down_revision: Union[str, None] = "0006_create_agent_memories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_agent_memories_source_turn_type",
        "agent_memories",
        ["user_id", "character", "source_turn_id", "memory_type"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_agent_memories_source_turn_type",
        "agent_memories",
        type_="unique",
    )
