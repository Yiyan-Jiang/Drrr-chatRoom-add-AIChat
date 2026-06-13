from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.knowledge.models import KnowledgeDocument, KnowledgeSection
from ai.models.knowledge_chunk import KnowledgeChunk as KnowledgeChunkRecord
from ai.models.knowledge_document import KnowledgeDocument as KnowledgeDocumentRecord
from ai.models.knowledge_job import KnowledgeJob as KnowledgeJobRecord
from ai.models.knowledge_section import KnowledgeSection as KnowledgeSectionRecord


class InMemoryKnowledgeStore:
    def __init__(
        self,
        documents: list[KnowledgeDocument] | None = None,
        sections: list[KnowledgeSection] | None = None,
    ):
        self._documents = {document.document_id: document for document in documents or []}
        self._sections = list(sections or [])

    def get_document(self, document_id: str) -> KnowledgeDocument:
        try:
            return self._documents[document_id]
        except KeyError as exc:
            raise ValueError(f"knowledge document not found: {document_id}") from exc

    def list_sections(self, document_id: str) -> list[KnowledgeSection]:
        return [section for section in self._sections if section.document_id == document_id]

    def get_sections(self, section_ids: list[str]) -> list[KnowledgeSection]:
        wanted = set(section_ids)
        return [section for section in self._sections if section.section_id in wanted]

    def all_sections(self) -> list[KnowledgeSection]:
        return list(self._sections)


async def create_knowledge_document(
    db: AsyncSession,
    document_id: str,
    title: str,
    source: str,
    owner_user_id: int,
    raw_content: str | None = None,
    now: datetime | None = None,
) -> KnowledgeDocumentRecord:
    current_time = now or datetime.now()
    document = KnowledgeDocumentRecord(
        document_id=document_id,
        title=title,
        source=source,
        owner_user_id=owner_user_id,
        status="active",
        raw_content=raw_content,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(document)
    await db.flush()
    return document


async def add_knowledge_section(
    db: AsyncSession,
    section_id: str,
    document_id: str,
    title: str,
    text: str,
    sequence_no: int,
    now: datetime | None = None,
) -> KnowledgeSectionRecord:
    current_time = now or datetime.now()
    section = KnowledgeSectionRecord(
        section_id=section_id,
        document_id=document_id,
        title=title,
        text=text,
        sequence_no=sequence_no,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(section)
    await db.flush()
    return section


async def add_knowledge_chunk(
    db: AsyncSession,
    chunk_id: str,
    document_id: str,
    section_id: str,
    text: str,
    sequence_no: int,
    lexical_terms: list[str] | None = None,
    now: datetime | None = None,
) -> KnowledgeChunkRecord:
    current_time = now or datetime.now()
    chunk = KnowledgeChunkRecord(
        chunk_id=chunk_id,
        document_id=document_id,
        section_id=section_id,
        text=text,
        sequence_no=sequence_no,
        lexical_terms=lexical_terms,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(chunk)
    await db.flush()
    return chunk


async def create_knowledge_job(
    db: AsyncSession,
    job_id: str,
    job_type: str,
    user_id: int,
    payload: dict | None = None,
    now: datetime | None = None,
) -> KnowledgeJobRecord:
    current_time = now or datetime.now()
    job = KnowledgeJobRecord(
        job_id=job_id,
        job_type=job_type,
        user_id=user_id,
        status="pending",
        payload=payload,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(job)
    await db.flush()
    return job


async def list_knowledge_sections(
    db: AsyncSession,
    document_id: str,
) -> list[KnowledgeSectionRecord]:
    result = await db.execute(
        select(KnowledgeSectionRecord)
        .where(KnowledgeSectionRecord.document_id == document_id)
        .order_by(KnowledgeSectionRecord.sequence_no)
    )
    return [
        section
        for section in result.scalars().all()
        if getattr(section, "document_id", None) == document_id
    ]


async def list_knowledge_chunks(
    db: AsyncSession,
    document_id: str,
) -> list[KnowledgeChunkRecord]:
    result = await db.execute(
        select(KnowledgeChunkRecord)
        .where(KnowledgeChunkRecord.document_id == document_id)
        .order_by(KnowledgeChunkRecord.sequence_no)
    )
    return [
        chunk
        for chunk in result.scalars().all()
        if getattr(chunk, "document_id", None) == document_id
    ]
