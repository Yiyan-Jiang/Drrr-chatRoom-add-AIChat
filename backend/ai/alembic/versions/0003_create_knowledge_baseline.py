"""create knowledge baseline

Revision ID: 0003_create_knowledge_baseline
Revises: 0002_create_agent_platform_state
Create Date: 2026-05-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_create_knowledge_baseline"
down_revision: Union[str, None] = "0002_create_agent_platform_state"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("document_id", name="uq_knowledge_documents_document_id"),
    )
    op.create_index("ix_knowledge_documents_document_id", "knowledge_documents", ["document_id"])
    op.create_index("ix_knowledge_documents_owner_user_id", "knowledge_documents", ["owner_user_id"])
    op.create_index("ix_knowledge_documents_status", "knowledge_documents", ["status"])

    op.create_table(
        "knowledge_sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section_id", sa.String(length=80), nullable=False),
        sa.Column("document_id", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("section_id", name="uq_knowledge_sections_section_id"),
        sa.UniqueConstraint("document_id", "sequence_no", name="uq_knowledge_sections_document_sequence"),
    )
    op.create_index("ix_knowledge_sections_section_id", "knowledge_sections", ["section_id"])
    op.create_index("ix_knowledge_sections_document_id", "knowledge_sections", ["document_id"])

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chunk_id", sa.String(length=80), nullable=False),
        sa.Column("document_id", sa.String(length=80), nullable=False),
        sa.Column("section_id", sa.String(length=80), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("lexical_terms", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("chunk_id", name="uq_knowledge_chunks_chunk_id"),
        sa.UniqueConstraint("section_id", "sequence_no", name="uq_knowledge_chunks_section_sequence"),
    )
    op.create_index("ix_knowledge_chunks_chunk_id", "knowledge_chunks", ["chunk_id"])
    op.create_index("ix_knowledge_chunks_document_id", "knowledge_chunks", ["document_id"])
    op.create_index("ix_knowledge_chunks_section_id", "knowledge_chunks", ["section_id"])

    op.create_table(
        "knowledge_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.String(length=80), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("job_id", name="uq_knowledge_jobs_job_id"),
    )
    op.create_index("ix_knowledge_jobs_job_id", "knowledge_jobs", ["job_id"])
    op.create_index("ix_knowledge_jobs_job_type", "knowledge_jobs", ["job_type"])
    op.create_index("ix_knowledge_jobs_user_id", "knowledge_jobs", ["user_id"])
    op.create_index("ix_knowledge_jobs_status", "knowledge_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_jobs_status", table_name="knowledge_jobs")
    op.drop_index("ix_knowledge_jobs_user_id", table_name="knowledge_jobs")
    op.drop_index("ix_knowledge_jobs_job_type", table_name="knowledge_jobs")
    op.drop_index("ix_knowledge_jobs_job_id", table_name="knowledge_jobs")
    op.drop_table("knowledge_jobs")

    op.drop_index("ix_knowledge_chunks_section_id", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_document_id", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_chunk_id", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")

    op.drop_index("ix_knowledge_sections_document_id", table_name="knowledge_sections")
    op.drop_index("ix_knowledge_sections_section_id", table_name="knowledge_sections")
    op.drop_table("knowledge_sections")

    op.drop_index("ix_knowledge_documents_status", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_documents_owner_user_id", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_documents_document_id", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
