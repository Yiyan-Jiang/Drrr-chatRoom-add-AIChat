"""normal initial schema

Revision ID: 0001_normal_initial_schema
Revises: None
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_normal_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chatRoom_user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("password", sa.String(length=128), nullable=True),
        sa.Column("avatar_key", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("username"),
    )
    op.create_index("idx_chatRoom_user_avatar_key", "chatRoom_user", ["avatar_key"])

    op.create_table(
        "chatRoom_room",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=8), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notice", sa.Text(), nullable=True),
        sa.Column("rules", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("min_age", sa.Integer(), nullable=True),
        sa.Column("max_age", sa.Integer(), nullable=True),
        sa.Column("max_members", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("peak_online_members", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["chatRoom_user.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("idx_chatRoom_room_owner_id", "chatRoom_room", ["owner_id"])

    op.create_table(
        "chatRoom_message",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("message_type", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column("client_message_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["chatRoom_room.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["chatRoom_user.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("client_message_id"),
    )
    op.create_index("idx_chatRoom_message_room_created_id", "chatRoom_message", ["room_id", "created_at", "id"])


def downgrade() -> None:
    op.drop_index("idx_chatRoom_message_room_created_id", table_name="chatRoom_message")
    op.drop_table("chatRoom_message")
    op.drop_index("idx_chatRoom_room_owner_id", table_name="chatRoom_room")
    op.drop_table("chatRoom_room")
    op.drop_index("idx_chatRoom_user_avatar_key", table_name="chatRoom_user")
    op.drop_table("chatRoom_user")
