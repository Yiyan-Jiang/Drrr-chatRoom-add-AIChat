from collections.abc import Awaitable, Callable
from typing import Any

from ai.database import get_ai_sessionmaker
from ai.knowledge.evidence import extract_evidence
from ai.knowledge.repositories import InMemoryKnowledgeStore
from ai.knowledge.retrieval import search_knowledge
from ai.repositories.artifact_repository import write_artifact
from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext, ToolPermission, ToolSpec

ArtifactWriter = Callable[[ToolExecutionContext, str, dict[str, Any]], Awaitable[Any]]


async def default_artifact_writer(
    ctx: ToolExecutionContext,
    artifact_type: str,
    payload: dict[str, Any],
):
    async with get_ai_sessionmaker()() as db:
        artifact = await write_artifact(
            db,
            run_id=ctx.run_id,
            session_id=ctx.session_id,
            request_id=None,
            user_id=ctx.user_id,
            artifact_type=artifact_type,
            payload=payload,
        )
        await db.commit()
        await db.refresh(artifact)
        return artifact


def register_knowledge_tools(
    registry: ToolRegistry,
    store: InMemoryKnowledgeStore,
    artifact_writer: ArtifactWriter | None = None,
) -> None:
    writer = artifact_writer or default_artifact_writer

    async def search_tool(ctx: ToolExecutionContext, args: dict) -> ToolResult:
        candidates = search_knowledge(
            store,
            query=args["query"],
            top_k=args.get("top_k", 10),
        )
        return ToolResult(
            tool_name="search_knowledge",
            call_id=ctx.call_id,
            ok=True,
            result_kind="knowledge_candidates",
            preview=f"found {len(candidates)} candidates",
            payload={"candidates": [candidate.to_dict() for candidate in candidates]},
            facts=[],
        )

    async def open_tool(ctx: ToolExecutionContext, args: dict) -> ToolResult:
        document = store.get_document(args["document_id"])
        sections = store.list_sections(document.document_id)
        return ToolResult(
            tool_name="open_knowledge_document",
            call_id=ctx.call_id,
            ok=True,
            result_kind="knowledge_document",
            preview=document.title,
            payload={
                "document_id": document.document_id,
                "title": document.title,
                "sections": [section.to_preview() for section in sections],
            },
            facts=[],
            document_id=document.document_id,
        )

    async def extract_tool(ctx: ToolExecutionContext, args: dict) -> ToolResult:
        evidence = extract_evidence(
            store,
            document_id=args["document_id"],
            section_ids=args["section_ids"],
            question=args.get("question", ""),
        )
        artifact = await writer(
            ctx,
            "response_refs",
            {"refs": [item.to_dict() for item in evidence.refs]},
        )
        return ToolResult(
            tool_name="extract_knowledge_evidence",
            call_id=ctx.call_id,
            ok=True,
            result_kind="evidence_pack",
            preview=f"extracted {len(evidence.refs)} refs",
            payload={"artifact_id": artifact.artifact_id},
            facts=[item.to_fact() for item in evidence.refs],
            document_id=args["document_id"],
        )

    registry.register(
        ToolSpec(
            name="search_knowledge",
            description="Search indexed knowledge candidates.",
            input_schema={"required": ["query"]},
            permission=ToolPermission(scope="knowledge:read"),
            normalize=lambda arguments: {
                "query": arguments["query"],
                "top_k": int(arguments.get("top_k", 10)),
            },
            execute=search_tool,
        )
    )
    registry.register(
        ToolSpec(
            name="open_knowledge_document",
            description="Open a knowledge document and list sections.",
            input_schema={"required": ["document_id"]},
            permission=ToolPermission(scope="knowledge:read"),
            normalize=lambda arguments: {"document_id": arguments["document_id"]},
            execute=open_tool,
        )
    )
    registry.register(
        ToolSpec(
            name="extract_knowledge_evidence",
            description="Extract response references from selected sections.",
            input_schema={"required": ["document_id", "section_ids", "question"]},
            permission=ToolPermission(scope="knowledge:read"),
            normalize=lambda arguments: {
                "document_id": arguments["document_id"],
                "section_ids": list(arguments["section_ids"]),
                "question": arguments.get("question", ""),
            },
            execute=extract_tool,
        )
    )
