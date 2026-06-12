from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolResult:
    tool_name: str
    call_id: str
    ok: bool
    result_kind: str
    preview: str
    payload: dict
    facts: list[dict] = field(default_factory=list)
    resource_id: str | None = None
    document_id: str | None = None
    job_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    elapsed_ms: int | None = None
