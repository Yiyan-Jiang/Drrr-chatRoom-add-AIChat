from ai.harness.actions import ToolCall


def was_same_tool_call_repeated_without_progress(
    call: ToolCall,
    events: list,
) -> bool:
    repeated_results = [
        event
        for event in events[-5:]
        if getattr(event, "event_type", None) == "tool_result"
        and event.payload.get("tool") == call.name
        and event.payload.get("arguments") == call.arguments
    ]
    return len(repeated_results) >= 2
