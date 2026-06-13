import unittest
from datetime import datetime
from pathlib import Path


class FakeScalarResult:
    def __init__(self, records):
        self._records = records

    def all(self):
        return self._records


class FakeExecuteResult:
    def __init__(self, records):
        self._records = records

    def scalar_one_or_none(self):
        return self._records[0] if self._records else None

    def scalars(self):
        return FakeScalarResult(self._records)


class FakeSession:
    def __init__(self, records=None):
        self.records = records or []
        self.added = []
        self.flushes = 0

    def add(self, record):
        self.added.append(record)
        self.records.append(record)

    async def execute(self, _statement):
        return FakeExecuteResult(list(self.records))

    async def flush(self):
        self.flushes += 1


class KnowledgeModelMigrationTest(unittest.TestCase):
    def test_knowledge_models_use_expected_table_names(self):
        from ai.models.knowledge_chunk import KnowledgeChunk
        from ai.models.knowledge_document import KnowledgeDocument
        from ai.models.knowledge_job import KnowledgeJob
        from ai.models.knowledge_section import KnowledgeSection

        self.assertEqual(KnowledgeDocument.__tablename__, "knowledge_documents")
        self.assertEqual(KnowledgeSection.__tablename__, "knowledge_sections")
        self.assertEqual(KnowledgeChunk.__tablename__, "knowledge_chunks")
        self.assertEqual(KnowledgeJob.__tablename__, "knowledge_jobs")
        self.assertIn("document_id", KnowledgeDocument.__table__.c)
        self.assertIn("section_id", KnowledgeSection.__table__.c)
        self.assertIn("chunk_id", KnowledgeChunk.__table__.c)
        self.assertIn("job_id", KnowledgeJob.__table__.c)

    def test_knowledge_migration_creates_baseline_tables(self):
        root = Path(__file__).resolve().parents[1]
        migration = root / "ai" / "alembic" / "versions" / "0003_create_knowledge_baseline.py"

        text = migration.read_text(encoding="utf-8")

        self.assertIn('revision: str = "0003_create_knowledge_baseline"', text)
        self.assertIn('down_revision: Union[str, None] = "0002_create_agent_platform_state"', text)
        self.assertIn('"knowledge_documents"', text)
        self.assertIn('"knowledge_sections"', text)
        self.assertIn('"knowledge_chunks"', text)
        self.assertIn('"knowledge_jobs"', text)


class KnowledgeRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_document_section_chunk_and_job_flush_without_commit(self):
        from ai.knowledge.repositories import (
            add_knowledge_chunk,
            add_knowledge_section,
            create_knowledge_document,
            create_knowledge_job,
        )

        session = FakeSession()
        now = datetime(2026, 5, 26, 12, 0, 0)

        document = await create_knowledge_document(
            session,
            document_id="doc-1",
            title="部署手册",
            source="test",
            owner_user_id=7,
            raw_content="部署步骤是安装依赖、运行迁移、启动服务。",
            now=now,
        )
        section = await add_knowledge_section(
            session,
            section_id="sec-1",
            document_id=document.document_id,
            title="部署步骤",
            text="部署步骤是安装依赖、运行迁移、启动服务。",
            sequence_no=1,
            now=now,
        )
        chunk = await add_knowledge_chunk(
            session,
            chunk_id="chunk-1",
            document_id=document.document_id,
            section_id=section.section_id,
            text=section.text,
            sequence_no=1,
            lexical_terms=["部署", "迁移"],
            now=now,
        )
        job = await create_knowledge_job(
            session,
            job_id="job-1",
            job_type="manual_ingest",
            user_id=7,
            payload={"document_id": document.document_id},
            now=now,
        )

        self.assertEqual(document.status, "active")
        self.assertEqual(section.document_id, "doc-1")
        self.assertEqual(chunk.lexical_terms, ["部署", "迁移"])
        self.assertEqual(job.status, "pending")
        self.assertEqual(session.flushes, 4)

    async def test_list_document_sections_returns_matching_sections(self):
        from ai.knowledge.repositories import list_knowledge_sections
        from ai.models.knowledge_section import KnowledgeSection

        section = KnowledgeSection(
            section_id="sec-1",
            document_id="doc-1",
            title="部署步骤",
            text="部署步骤是安装依赖。",
            sequence_no=1,
        )
        session = FakeSession(records=[section])

        sections = await list_knowledge_sections(session, "doc-1")

        self.assertEqual(sections, [section])


if __name__ == "__main__":
    unittest.main()
