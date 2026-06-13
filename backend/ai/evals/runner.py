from dataclasses import dataclass

from ai.evals.assertions import assert_snapshot_expectations
from ai.evals.cases import ReplayCase
from ai.evals.debug import build_debug_snapshot
from ai.evals.replay import ReplayPlanner
from ai.harness.permissions import EffectivePolicy
from ai.harness.runtime import HarnessRuntime


@dataclass
class ReplayRunResult:
    case_id: str
    status: str
    repository: object
    result: object | None = None
    error: str | None = None


class InMemoryReplayRepository:
    def __init__(self, replay_case: ReplayCase):
        case_input = replay_case.input
        self.run = type(
            "Run",
            (),
            {
                "run_id": "run-1",
                "request_id": case_input.get("request_id", replay_case.case_id),
                "session_id": case_input.get("session_id", "session-1"),
                "user_id": case_input.get("user_id", 7),
                "status": "created",
                "checkpoint_payload": None,
                "skill_state_payload": None,
                "created_at": None,
                "completed_at": None,
            },
        )()
        self.audit = type(
            "Audit",
            (),
            {
                "request_id": self.run.request_id,
                "session_id": self.run.session_id,
                "user_id": self.run.user_id,
                "status": "completed",
                "stage": "completed",
                "error_code": None,
                "error_message": None,
                "debug_payload": None,
            },
        )()
        self.events = []
        self.artifacts = []

    async def load_or_create_run(self, _workspace):
        return self.run

    async def list_events(self, _run_id):
        return list(self.events)

    async def list_artifacts(self, _run_id):
        return list(self.artifacts)

    async def get_audit_by_request_id(self, _request_id):
        return self.audit

    async def append_event(self, run_id, event_type, payload):
        event = type(
            "Event",
            (),
            {
                "run_id": run_id,
                "sequence_no": len(self.events) + 1,
                "event_type": event_type,
                "payload": payload,
            },
        )()
        self.events.append(event)
        return event

    async def update_checkpoint(self, run, checkpoint):
        run.checkpoint_payload = checkpoint
        await self.append_event(run.run_id, "checkpoint_updated", {"checkpoint": checkpoint})
        return run

    async def update_skill_state(self, run, skill_state):
        run.skill_state_payload = skill_state
        return run

    async def write_artifact(self, run, artifact_type, payload, request_id=None):
        artifact = type(
            "Artifact",
            (),
            {
                "artifact_id": f"artifact-{len(self.artifacts) + 1}",
                "artifact_type": artifact_type,
                "payload": payload,
                "request_id": request_id or run.request_id,
            },
        )()
        self.artifacts.append(artifact)
        await self.append_event(
            run.run_id,
            "artifact_written",
            {"artifact_id": artifact.artifact_id, "artifact_type": artifact_type},
        )
        return artifact

    async def mark_terminal(self, run, status):
        run.status = status
        return run

    async def mark_failed(self, run, error_code, error_message):
        run.status = "failed"
        self.audit.status = "failed"
        self.audit.error_code = error_code
        self.audit.error_message = error_message
        return run


def _workspace(replay_case: ReplayCase):
    case_input = replay_case.input
    command = type(
        "Command",
        (),
        {
            "request_id": case_input.get("request_id", replay_case.case_id),
            "session_id": case_input.get("session_id", "session-1"),
            "user_id": case_input.get("user_id", 7),
            "message": case_input.get("message", ""),
            "character": case_input.get("character"),
            "metadata": case_input.get("metadata") or {},
        },
    )()
    session = type(
        "Session",
        (),
        {"session_id": command.session_id or "session-1", "user_id": command.user_id},
    )()
    return type("Workspace", (), {"command": command, "session": session, "recent_turns": []})()


def _policy(replay_case: ReplayCase) -> EffectivePolicy:
    policy = replay_case.policy or {}
    return EffectivePolicy(
        allowed_tools=list(policy.get("allowed_tools") or ["open_skill", "list_skills"]),
        ask_tools=list(policy.get("ask_tools") or []),
        denied_tools=list(policy.get("denied_tools") or []),
    )


async def run_replay_case(replay_case: ReplayCase) -> ReplayRunResult:
    repository = InMemoryReplayRepository(replay_case)
    runtime = HarnessRuntime(
        repository=repository,
        planner=ReplayPlanner(replay_case.planner_actions),
        policy=_policy(replay_case),
    )
    try:
        result = await runtime.run_turn(_workspace(replay_case))
        snapshot = await build_debug_snapshot(repository, "run-1")
        assert_snapshot_expectations(snapshot, replay_case.expected)
        return ReplayRunResult(
            case_id=replay_case.case_id,
            status="passed",
            repository=repository,
            result=result,
        )
    except Exception as exc:
        return ReplayRunResult(
            case_id=replay_case.case_id,
            status="failed",
            repository=repository,
            error=str(exc),
        )
