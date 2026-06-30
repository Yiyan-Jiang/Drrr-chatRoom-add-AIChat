"""create posts

Revision ID: 0003_create_posts
Revises: 0002_add_user_profile_fields
Create Date: 2026-06-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_create_posts"
down_revision: Union[str, None] = "0002_add_user_profile_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chatRoom_post",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["chatRoom_user.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_chatRoom_post_author_id", "chatRoom_post", ["author_id"])
    op.create_index("idx_chatRoom_post_status", "chatRoom_post", ["status"])

    op.create_table(
        "chatRoom_post_comment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["chatRoom_post.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["chatRoom_user.id"], ondelete="SET NULL"),
    )
    op.create_index("idx_chatRoom_post_comment_post_id", "chatRoom_post_comment", ["post_id"])
    op.create_index("idx_chatRoom_post_comment_author_id", "chatRoom_post_comment", ["author_id"])

    op.create_table(
        "chatRoom_post_like",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["chatRoom_post.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_like_post_user"),
    )
    op.create_index("idx_chatRoom_post_like_post_id", "chatRoom_post_like", ["post_id"])
    op.create_index("idx_chatRoom_post_like_user_id", "chatRoom_post_like", ["user_id"])

    op.create_table(
        "chatRoom_post_favorite",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["chatRoom_post.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["chatRoom_user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_favorite_post_user"),
    )
    op.create_index("idx_chatRoom_post_favorite_post_id", "chatRoom_post_favorite", ["post_id"])
    op.create_index("idx_chatRoom_post_favorite_user_id", "chatRoom_post_favorite", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_chatRoom_post_favorite_user_id", table_name="chatRoom_post_favorite")
    op.drop_index("idx_chatRoom_post_favorite_post_id", table_name="chatRoom_post_favorite")
    op.drop_table("chatRoom_post_favorite")
    op.drop_index("idx_chatRoom_post_like_user_id", table_name="chatRoom_post_like")
    op.drop_index("idx_chatRoom_post_like_post_id", table_name="chatRoom_post_like")
    op.drop_table("chatRoom_post_like")
    op.drop_index("idx_chatRoom_post_comment_author_id", table_name="chatRoom_post_comment")
    op.drop_index("idx_chatRoom_post_comment_post_id", table_name="chatRoom_post_comment")
    op.drop_table("chatRoom_post_comment")
    op.drop_index("idx_chatRoom_post_status", table_name="chatRoom_post")
    op.drop_index("idx_chatRoom_post_author_id", table_name="chatRoom_post")
    op.drop_table("chatRoom_post")
