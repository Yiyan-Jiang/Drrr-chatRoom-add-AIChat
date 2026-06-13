"""repair harness run skill state column

Revision ID: 0005_harness_skill_state
Revises: 0004_create_governance_baseline
Create Date: 2026-05-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_harness_skill_state"
down_revision: Union[str, None] = "0004_create_governance_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(
        column["name"] == column_name
        for column in inspector.get_columns(table_name)
    )


def upgrade() -> None:
    if not _has_column("harness_runs", "skill_state_payload"):
        op.add_column(
            "harness_runs",
            sa.Column("skill_state_payload", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    if _has_column("harness_runs", "skill_state_payload"):
        op.drop_column("harness_runs", "skill_state_payload")
