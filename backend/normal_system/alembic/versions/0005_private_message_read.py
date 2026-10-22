"""为私聊消息增加服务端已读时间。"""

from alembic import op
import sqlalchemy as sa

revision = "0005_private_message_read"
down_revision = "0004_create_friends_private_chat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """增加已读时间，历史消息在首次阅读前保持未读。"""
    op.add_column(
        "chatRoom_private_message", sa.Column("read_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """移除已读时间字段。"""
    op.drop_column("chatRoom_private_message", "read_at")
