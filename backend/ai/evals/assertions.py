def assert_benchmark_expectations(
    events: list,
    artifacts: list,
    result,
    expected: dict,
) -> None:
    tools_called = [
        event.payload.get("tool")
        for event in events
        if getattr(event, "event_type", None) == "tool_call_requested"
    ]
    artifact_types = [artifact.artifact_type for artifact in artifacts]
    status = result.metadata.get("status")

    for tool in expected.get("required_tools", []):
        if tool not in tools_called:
            raise AssertionError(f"required tool not called: {tool}")

    for artifact_type in expected.get("required_artifacts", []):
        if artifact_type not in artifact_types:
            raise AssertionError(f"required artifact missing: {artifact_type}")

    expected_status = expected.get("final_status")
    if expected_status is not None and status != expected_status:
        raise AssertionError(f"expected status {expected_status}, got {status}")

    answer = result.answer or ""
    for text in expected.get("answer_contains", []):
        if text not in answer:
            raise AssertionError(f"answer missing expected text: {text}")


def assert_snapshot_expectations(snapshot: dict, expected: dict) -> None:
    opened_skills = {
        skill.get("name")
        for skill in (snapshot.get("skill_state") or {}).get("opened_skills", [])
    }
    for skill_name in expected.get("required_skills", []):
        if skill_name not in opened_skills:
            raise AssertionError(f"required skill missing: {skill_name}")

    action_types = [action.get("type") for action in snapshot.get("planner_actions", [])]
    for action_type in expected.get("required_actions", []):
        if action_type not in action_types:
            raise AssertionError(f"required action missing: {action_type}")

    tools_called = [item.get("tool") for item in snapshot.get("tool_timeline", [])]
    for tool_name in expected.get("required_tools", []):
        if tool_name not in tools_called:
            raise AssertionError(f"required tool not called: {tool_name}")
    for tool_name in expected.get("forbidden_tools", []):
        if tool_name in tools_called:
            raise AssertionError(f"forbidden tool called: {tool_name}")

    permissions = {
        item.get("tool"): (item.get("permission") or {}).get("kind")
        for item in snapshot.get("tool_timeline", [])
    }
    for tool_name, decision in expected.get("required_permissions", {}).items():
        if permissions.get(tool_name) != decision:
            raise AssertionError(
                f"expected permission {decision} for {tool_name}, got {permissions.get(tool_name)}"
            )

    artifact_types = [item.get("artifact_type") for item in snapshot.get("artifact_timeline", [])]
    for artifact_type in expected.get("required_artifacts", []):
        if artifact_type not in artifact_types:
            raise AssertionError(f"required artifact missing: {artifact_type}")
    for artifact_type in expected.get("forbidden_artifacts", []):
        if artifact_type in artifact_types:
            raise AssertionError(f"forbidden artifact written: {artifact_type}")

    checkpoint = snapshot.get("checkpoint") or {}
    for key, value in expected.get("checkpoint_contains", {}).items():
        if checkpoint.get(key) != value:
            raise AssertionError(f"checkpoint mismatch for {key}: expected {value}, got {checkpoint.get(key)}")
    for path in expected.get("checkpoint_path_exists", []):
        if _read_path(checkpoint, path) is None:
            raise AssertionError(f"checkpoint path missing: {path}")

    expected_status = expected.get("final_status")
    if expected_status is not None and (snapshot.get("run") or {}).get("status") != expected_status:
        raise AssertionError(
            f"expected status {expected_status}, got {(snapshot.get('run') or {}).get('status')}"
        )

    _assert_event_sequence(
        [event.get("event_type") for event in snapshot.get("events", [])],
        expected.get("event_sequence", []),
    )

    expected_error_layer = expected.get("error_layer")
    if expected_error_layer is not None:
        layers = [error.get("layer") for error in snapshot.get("errors", [])]
        if expected_error_layer not in layers:
            raise AssertionError(f"expected error layer {expected_error_layer}, got {layers}")


def _read_path(payload: dict, path: str):
    current = payload
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _assert_event_sequence(actual: list[str], expected: list[str]) -> None:
    cursor = 0
    for event_type in actual:
        if cursor < len(expected) and event_type == expected[cursor]:
            cursor += 1
    if cursor != len(expected):
        raise AssertionError(f"event sequence missing: {expected}")
