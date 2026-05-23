"""create ai chat history

Revision ID: 0001_create_ai_chat_history
Revises: None
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_ai_chat_history"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_chat_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("character", sa.String(length=20), nullable=False, server_default="sakura"),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_chat_history_user_id", "ai_chat_history", ["user_id"])
    op.create_index("ix_ai_chat_history_character", "ai_chat_history", ["character"])


def downgrade() -> None:
    op.drop_index("ix_ai_chat_history_character", table_name="ai_chat_history")
    op.drop_index("ix_ai_chat_history_user_id", table_name="ai_chat_history")
    op.drop_table("ai_chat_history")
