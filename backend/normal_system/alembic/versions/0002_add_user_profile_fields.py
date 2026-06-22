"""add user profile fields

Revision ID: 0002_add_user_profile_fields
Revises: 0001_normal_initial_schema
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_add_user_profile_fields"
down_revision: Union[str, None] = "0001_normal_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chatRoom_user", sa.Column("nickname", sa.String(length=64), nullable=True))
    op.add_column("chatRoom_user", sa.Column("bio", sa.String(length=200), nullable=False, server_default=""))
    op.execute("UPDATE chatRoom_user SET nickname = username WHERE nickname IS NULL")
    op.alter_column(
        "chatRoom_user",
        "nickname",
        existing_type=sa.String(length=64),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("chatRoom_user", "bio")
    op.drop_column("chatRoom_user", "nickname")
