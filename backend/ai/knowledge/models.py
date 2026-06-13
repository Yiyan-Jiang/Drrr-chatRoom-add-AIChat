from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    title: str
    source: str
    owner_user_id: int
    status: str = "active"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeSection:
    section_id: str
    document_id: str
    title: str
    text: str

    def to_preview(self) -> dict:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "preview": self.text[:160],
        }


@dataclass(frozen=True)
class KnowledgeCandidate:
    document_id: str
    section_id: str
    title: str
    snippet: str
    score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceRef:
    document_id: str
    section_id: str
    quote: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_fact(self) -> dict:
        return {
            "document_id": self.document_id,
            "section_id": self.section_id,
            "claim": self.quote,
        }


@dataclass(frozen=True)
class EvidenceExtraction:
    refs: list[EvidenceRef]
