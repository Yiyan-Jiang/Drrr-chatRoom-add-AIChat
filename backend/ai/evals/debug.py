from dataclasses import asdict, is_dataclass


def _to_payload(value):
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return value


def _sequence_no(event) -> int | None:
    return getattr(event, "sequence_no", None)


def _event_payload(event) -> dict:
    payload = _to_payload(getattr(event, "payload", {}))
    return payload if isinstance(payload, dict) else {"value": payload}


def _event_dict(event) -> dict:
    return {
        "sequence_no": _sequence_no(event),
        "event_type": event.event_type,
        "payload": _event_payload(event),
    }


def _run_payload(run, run_id: str) -> dict:
    return {
        "run_id": run_id,
        "request_id": getattr(run, "request_id", None),
        "session_id": getattr(run, "session_id", None),
        "user_id": getattr(run, "user_id", None),
        "status": getattr(run, "status", None),
        "trace_id": run_id,
        "created_at": str(getattr(run, "created_at", "")) if getattr(run, "created_at", None) else None,
        "completed_at": str(getattr(run, "completed_at", "")) if getattr(run, "completed_at", None) else None,
    }


async def _request_trace(repository, run) -> dict | None:
    request_id = getattr(run, "request_id", None)
    audit = None
    if request_id and hasattr(repository, "get_audit_by_request_id"):
        audit = await repository.get_audit_by_request_id(request_id)
    if audit is None:
        audit = getattr(repository, "audit", None)
    if audit is None:
        return None
    return {
        "request_id": getattr(audit, "request_id", request_id),
        "session_id": getattr(audit, "session_id", getattr(run, "session_id", None)),
        "user_id": getattr(audit, "user_id", getattr(run, "user_id", None)),
        "status": getattr(audit, "status", None),
        "stage": getattr(audit, "stage", None),
        "error_code": getattr(audit, "error_code", None),
        "error_message": getattr(audit, "error_message", None),
        "debug_payload": _to_payload(getattr(audit, "debug_payload", None)),
    }


def _planner_actions(event_rows: list[dict]) -> list[dict]:
    actions = []
    for event in event_rows:
        if event["event_type"] != "planner_action":
            continue
        payload = event["payload"]
        action = dict(payload)
        action["sequence_no"] = event["sequence_no"]
        actions.append(action)
    return actions


def _context_ledger(event_rows: list[dict]) -> list[dict]:
    for event in event_rows:
        if event["event_type"] == "context_compiled":
            return list(event["payload"].get("ledger") or [])
    return []


def _tool_timeline(event_rows: list[dict]) -> list[dict]:
    by_call: dict[str, dict] = {}
    for event in event_rows:
        payload = event["payload"]
        call_id = payload.get("call_id")
        if not call_id:
            continue
        item = by_call.setdefault(
            call_id,
            {"call_id": call_id, "sequence_no": event["sequence_no"]},
        )
        if event["event_type"] == "tool_call_requested":
            item.update(
                {
                    "tool": payload.get("tool"),
                    "arguments": payload.get("arguments"),
                    "requested": payload,
                }
            )
        elif event["event_type"] == "permission_decision":
            item["tool"] = item.get("tool") or payload.get("tool")
            item["permission"] = payload.get("decision")
        elif event["event_type"] == "tool_result":
            item["tool"] = item.get("tool") or payload.get("tool")
            item["arguments"] = item.get("arguments") or payload.get("arguments")
            item["result"] = payload.get("result")
    return sorted(by_call.values(), key=lambda item: item.get("sequence_no") or 0)


def _permission_timeline(event_rows: list[dict]) -> list[dict]:
    return [
        {
            "sequence_no": event["sequence_no"],
            "call_id": event["payload"].get("call_id"),
            "tool": event["payload"].get("tool"),
            "decision": event["payload"].get("decision"),
        }
        for event in event_rows
        if event["event_type"] == "permission_decision"
    ]


def _artifact_timeline(event_rows: list[dict], artifacts: list) -> list[dict]:
    timeline = [
        {
            "sequence_no": event["sequence_no"],
            "artifact_id": event["payload"].get("artifact_id"),
            "artifact_type": event["payload"].get("artifact_type"),
        }
        for event in event_rows
        if event["event_type"] == "artifact_written"
    ]
    if timeline:
        return timeline
    return [
        {
            "sequence_no": None,
            "artifact_type": artifact.artifact_type,
        }
        for artifact in artifacts
    ]


def _checkpoint_history(event_rows: list[dict]) -> list[dict]:
    return [
        {
            "sequence_no": event["sequence_no"],
            "checkpoint": event["payload"].get("checkpoint"),
        }
        for event in event_rows
        if event["event_type"] == "checkpoint_updated"
    ]


def _skill_timeline(event_rows: list[dict]) -> list[dict]:
    return [
        {
            "sequence_no": event["sequence_no"],
            "event_type": event["event_type"],
            "payload": event["payload"],
        }
        for event in event_rows
        if event["event_type"] in {"skill_opened", "skill_policy_merged", "skill_contract_rejected"}
    ]


def _errors(event_rows: list[dict], request: dict | None) -> list[dict]:
    errors = []
    if request and request.get("error_code"):
        errors.append(
            {
                "layer": "request",
                "error_code": request.get("error_code"),
                "error_message": request.get("error_message"),
                "stage": request.get("stage"),
            }
        )
    for event in event_rows:
        event_type = event["event_type"]
        payload = event["payload"]
        if event_type == "planner_invalid_action":
            errors.append({"layer": "planner", "event": event})
        elif event_type == "skill_contract_rejected":
            errors.append({"layer": "skill", "event": event})
        elif event_type == "permission_decision":
            decision = payload.get("decision") or {}
            if decision.get("kind") == "deny":
                errors.append({"layer": "permission", "event": event})
        elif event_type == "tool_result":
            result = payload.get("result") or {}
            if result.get("ok") is False:
                errors.append(
                    {
                        "layer": "tool",
                        "tool": payload.get("tool"),
                        "error_code": result.get("error_code"),
                        "error_message": result.get("error_message"),
                        "event": event,
                    }
                )
    return errors


async def build_debug_snapshot(repository, run_id: str) -> dict:
    events = await repository.list_events(run_id)
    artifacts = await repository.list_artifacts(run_id)
    run = getattr(repository, "run", None)
    checkpoint = getattr(run, "checkpoint_payload", None)
    event_rows = [_event_dict(event) for event in events]
    request = await _request_trace(repository, run) if run is not None else None

    return {
        "run_id": run_id,
        "request": request,
        "run": _run_payload(run, run_id) if run is not None else {"run_id": run_id},
        "checkpoint": checkpoint,
        "context_ledger": _context_ledger(event_rows),
        "planner_actions": _planner_actions(event_rows),
        "tool_timeline": _tool_timeline(event_rows),
        "permission_timeline": _permission_timeline(event_rows),
        "artifact_timeline": _artifact_timeline(event_rows, artifacts),
        "checkpoint_history": _checkpoint_history(event_rows),
        "skill_state": _to_payload(getattr(run, "skill_state_payload", None)) or {},
        "skill_timeline": _skill_timeline(event_rows),
        "events": event_rows,
        "artifacts": [
            {
                "artifact_type": artifact.artifact_type,
                "payload": _to_payload(artifact.payload),
            }
            for artifact in artifacts
        ],
        "errors": _errors(event_rows, request),
    }
