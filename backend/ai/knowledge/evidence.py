from ai.knowledge.models import EvidenceExtraction, EvidenceRef
from ai.knowledge.repositories import InMemoryKnowledgeStore


def extract_evidence(
    store: InMemoryKnowledgeStore,
    document_id: str,
    section_ids: list[str],
    question: str,
) -> EvidenceExtraction:
    refs = [
        EvidenceRef(
            document_id=document_id,
            section_id=section.section_id,
            quote=section.text,
        )
        for section in store.get_sections(section_ids)
        if section.document_id == document_id
    ]
    return EvidenceExtraction(refs=refs)
