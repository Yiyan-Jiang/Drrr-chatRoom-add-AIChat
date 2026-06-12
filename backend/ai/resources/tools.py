from ai.resources.models import AgentResource
from ai.resources.visibility import can_see_resource
from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolPermission, ToolSpec


def register_resource_tools(
    registry: ToolRegistry,
    resources: list[AgentResource],
) -> None:
    async def list_resources(ctx, args: dict) -> ToolResult:
        workspace = args["workspace"]
        visible = [resource for resource in resources if can_see_resource(workspace, resource)]
        return ToolResult(
            tool_name="list_resources",
            call_id=ctx.call_id,
            ok=True,
            result_kind="resource_list",
            preview=f"{len(visible)} resource(s)",
            payload={"resources": [resource.to_preview() for resource in visible]},
            facts=[],
        )

    async def open_resource(ctx, args: dict) -> ToolResult:
        workspace = args["workspace"]
        resource_id = args["resource_id"]
        for resource in resources:
            if resource.resource_id == resource_id and can_see_resource(workspace, resource):
                return ToolResult(
                    tool_name="open_resource",
                    call_id=ctx.call_id,
                    ok=True,
                    result_kind="resource",
                    preview=resource.title,
                    payload=resource.to_dict(),
                    facts=[],
                    resource_id=resource.resource_id,
                )
        return ToolResult(
            tool_name="open_resource",
            call_id=ctx.call_id,
            ok=False,
            result_kind="not_found",
            preview="resource not visible",
            payload={},
            facts=[],
            resource_id=resource_id,
            error_code="RESOURCE_NOT_VISIBLE",
            error_message="resource not visible",
        )

    registry.register(
        ToolSpec(
            name="list_resources",
            description="List resources visible to the current workspace.",
            input_schema={},
            permission=ToolPermission(scope="resource:read"),
            normalize=lambda arguments: arguments,
            execute=list_resources,
        )
    )
    registry.register(
        ToolSpec(
            name="open_resource",
            description="Open a visible resource.",
            input_schema={"required": ["resource_id"]},
            permission=ToolPermission(scope="resource:read"),
            normalize=lambda arguments: arguments,
            execute=open_resource,
        )
    )
