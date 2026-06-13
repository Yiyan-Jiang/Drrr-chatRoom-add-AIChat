from ai.knowledge.models import KnowledgeCandidate
from ai.knowledge.repositories import InMemoryKnowledgeStore


def _score(query: str, text: str) -> float:
    if not query:
        return 0.0
    if query in text:
        return float(len(query) + 10)
    query_chars = {char for char in query if not char.isspace()}
    text_chars = {char for char in text if not char.isspace()}
    if not query_chars:
        return 0.0
    return len(query_chars & text_chars) / len(query_chars)


def search_knowledge(
    store: InMemoryKnowledgeStore,
    query: str,
    top_k: int = 10,
) -> list[KnowledgeCandidate]:
    candidates: list[KnowledgeCandidate] = []
    for section in store.all_sections():
        score = _score(query, f"{section.title}\n{section.text}")
        if score <= 0:
            continue
        document = store.get_document(section.document_id)
        candidates.append(
            KnowledgeCandidate(
                document_id=document.document_id,
                section_id=section.section_id,
                title=document.title,
                snippet=section.text[:180],
                score=score,
            )
        )

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[:top_k]
