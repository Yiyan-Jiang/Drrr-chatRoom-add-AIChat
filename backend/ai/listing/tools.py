from collections.abc import Awaitable, Callable
from typing import Any

from ai.listing.models import ListingItem
from ai.listing.search import listing_search
from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext, ToolPermission, ToolSpec

ArtifactWriter = Callable[[ToolExecutionContext, str, dict[str, Any]], Awaitable[Any]]


def register_listing_tools(
    registry: ToolRegistry,
    items: list[ListingItem],
    artifact_writer: ArtifactWriter,
) -> None:
    async def search_tool(ctx: ToolExecutionContext, args: dict) -> ToolResult:
        result = listing_search(items, args.get("query", ""))
        artifact = await artifact_writer(ctx, "listing_state", result.to_dict())
        return ToolResult(
            tool_name="listing_search",
            call_id=ctx.call_id,
            ok=True,
            result_kind="listing_result",
            preview=f"{len(result.items)} item(s)",
            payload={"artifact_id": artifact.artifact_id, **result.to_dict()},
            facts=[],
        )

    registry.register(
        ToolSpec(
            name="listing_search",
            description="Search listing items and store active listing state.",
            input_schema={"required": ["query"]},
            permission=ToolPermission(scope="listing:read"),
            normalize=lambda arguments: {"query": arguments.get("query", "")},
            execute=search_tool,
        )
    )
