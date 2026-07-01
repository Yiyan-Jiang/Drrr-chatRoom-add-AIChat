"""create friends private chat

Revision ID: 0004_create_friends_private_chat
Revises: 0003_create_posts
Create Date: 2026-07-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_create_friends_private_chat"
down_revision: Union[str, None] = "0003_create_posts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chatRoom_friend_request",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["requester_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("requester_id", "recipient_id", "status", name="uq_friend_request_direction_status"),
    )
    op.create_index("idx_chatRoom_friend_request_requester_id", "chatRoom_friend_request", ["requester_id"])
    op.create_index("idx_chatRoom_friend_request_recipient_id", "chatRoom_friend_request", ["recipient_id"])
    op.create_index("idx_chatRoom_friend_request_status", "chatRoom_friend_request", ["status"])

    op.create_table(
        "chatRoom_friendship",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_low_id", sa.Integer(), nullable=False),
        sa.Column("user_high_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_low_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_high_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_pair"),
    )
    op.create_index("idx_chatRoom_friendship_user_low_id", "chatRoom_friendship", ["user_low_id"])
    op.create_index("idx_chatRoom_friendship_user_high_id", "chatRoom_friendship", ["user_high_id"])

    op.create_table(
        "chatRoom_private_message",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("client_message_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("client_message_id", name="uq_private_message_client_message_id"),
    )
    op.create_index("idx_chatRoom_private_message_sender_id", "chatRoom_private_message", ["sender_id"])
    op.create_index("idx_chatRoom_private_message_recipient_id", "chatRoom_private_message", ["recipient_id"])
    op.create_index("idx_chatRoom_private_message_created_at", "chatRoom_private_message", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_chatRoom_private_message_created_at", table_name="chatRoom_private_message")
    op.drop_index("idx_chatRoom_private_message_recipient_id", table_name="chatRoom_private_message")
    op.drop_index("idx_chatRoom_private_message_sender_id", table_name="chatRoom_private_message")
    op.drop_table("chatRoom_private_message")
    op.drop_index("idx_chatRoom_friendship_user_high_id", table_name="chatRoom_friendship")
    op.drop_index("idx_chatRoom_friendship_user_low_id", table_name="chatRoom_friendship")
    op.drop_table("chatRoom_friendship")
    op.drop_index("idx_chatRoom_friend_request_status", table_name="chatRoom_friend_request")
    op.drop_index("idx_chatRoom_friend_request_recipient_id", table_name="chatRoom_friend_request")
    op.drop_index("idx_chatRoom_friend_request_requester_id", table_name="chatRoom_friend_request")
    op.drop_table("chatRoom_friend_request")
