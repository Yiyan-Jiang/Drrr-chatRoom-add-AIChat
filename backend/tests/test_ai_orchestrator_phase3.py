import unittest

from ai.repositories.agent_audit_repository import RequestReservation


class FakeDeps:
    def __init__(self, reservation):
        self.reservation = reservation
        self.calls = []
        self.session_error = None
        self.turn_error = None

    async def reserve_request(self, command):
        self.calls.append(("reserve", command.request_id))
        return self.reservation

    async def mark_running(self, request_id, stage):
        self.calls.append(("running", request_id, stage))

    async def mark_failed(self, request_id, stage, error_code, error_message):
        self.calls.append(("failed", request_id, stage, error_code, error_message))

    async def load_or_create_session(self, command):
        self.calls.append(("session", command.session_id, command.user_id))
        if self.session_error is not None:
            raise self.session_error
        return type(
            "Session",
            (),
            {
                "session_id": command.session_id or "s-created",
                "user_id": command.user_id,
            },
        )()

    async def run_locked_turn(self, command, session, mark_stage):
        self.calls.append(("locked_turn", command.request_id, session.session_id))
        if self.turn_error is not None:
            await mark_stage("persisting")
            raise self.turn_error
        from ai.orchestrator.schemas import AITurnResult

        return AITurnResult(
            request_id=command.request_id,
            session_id=session.session_id,
            answer=f"fake: {command.message}",
            status="completed",
        )


class AIOrchestratorPhase3Test(unittest.IsolatedAsyncioTestCase):
    async def test_completed_reservation_returns_cached_response_without_running(self):
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        deps = FakeDeps(
            RequestReservation(
                kind="completed",
                response_payload={
                    "request_id": "request-1",
                    "session_id": "s-1",
                    "answer": "cached",
                    "status": "completed",
                },
            )
        )
        orchestrator = AITurnOrchestrator(deps)

        result = await orchestrator.handle_turn(
            AITurnCommand(
                request_id="request-1",
                session_id="s-1",
                user_id=7,
                message="hello",
                character="rin",
                metadata={},
            )
        )

        self.assertEqual(result.answer, "cached")
        self.assertEqual(deps.calls, [("reserve", "request-1")])

    async def test_accepted_turn_loads_session_then_runs_locked_turn(self):
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        deps = FakeDeps(RequestReservation(kind="accepted"))
        orchestrator = AITurnOrchestrator(deps)

        result = await orchestrator.handle_turn(
            AITurnCommand(
                request_id="request-2",
                session_id=None,
                user_id=7,
                message="hello",
                character=None,
                metadata={},
            )
        )

        self.assertEqual(result.session_id, "s-created")
        self.assertEqual(result.answer, "fake: hello")
        self.assertEqual(
            deps.calls,
            [
                ("reserve", "request-2"),
                ("running", "request-2", "session_loading"),
                ("session", None, 7),
                ("running", "request-2", "runtime_running"),
                ("locked_turn", "request-2", "s-created"),
            ],
        )

    async def test_in_progress_reservation_raises_structured_error(self):
        from ai.orchestrator.errors import RequestInProgress
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        orchestrator = AITurnOrchestrator(FakeDeps(RequestReservation(kind="in_progress")))

        with self.assertRaises(RequestInProgress) as error:
            await orchestrator.handle_turn(
                AITurnCommand(
                    request_id="request-3",
                    session_id="s-1",
                    user_id=7,
                    message="hello",
                    character=None,
                    metadata={},
                )
            )

        self.assertEqual(error.exception.error_code, "REQUEST_IN_PROGRESS")

    async def test_failed_reservation_raises_structured_previous_failure(self):
        from ai.orchestrator.errors import PreviousRequestFailed
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        orchestrator = AITurnOrchestrator(
            FakeDeps(RequestReservation(kind="failed", error_code="MODEL_TIMEOUT"))
        )

        with self.assertRaises(PreviousRequestFailed) as error:
            await orchestrator.handle_turn(
                AITurnCommand(
                    request_id="request-4",
                    session_id="s-1",
                    user_id=7,
                    message="hello",
                    character=None,
                    metadata={},
                )
            )

        self.assertEqual(error.exception.error_code, "PREVIOUS_REQUEST_FAILED")

    async def test_session_failure_marks_audit_failed_at_session_loading_stage(self):
        from ai.orchestrator.errors import SessionNotFound
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        deps = FakeDeps(RequestReservation(kind="accepted"))
        deps.session_error = SessionNotFound("missing")
        orchestrator = AITurnOrchestrator(deps)

        with self.assertRaises(SessionNotFound):
            await orchestrator.handle_turn(
                AITurnCommand(
                    request_id="request-5",
                    session_id="s-missing",
                    user_id=7,
                    message="hello",
                    character=None,
                    metadata={},
                )
            )

        self.assertEqual(
            deps.calls,
            [
                ("reserve", "request-5"),
                ("running", "request-5", "session_loading"),
                ("session", "s-missing", 7),
                ("failed", "request-5", "session_loading", "SESSION_NOT_FOUND", "missing"),
            ],
        )

    async def test_locked_turn_failure_marks_audit_failed_at_persisting_stage(self):
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import AITurnOrchestrator

        deps = FakeDeps(RequestReservation(kind="accepted"))
        deps.turn_error = RuntimeError("persist failed")
        orchestrator = AITurnOrchestrator(deps)

        with self.assertRaises(RuntimeError):
            await orchestrator.handle_turn(
                AITurnCommand(
                    request_id="request-6",
                    session_id="s-1",
                    user_id=7,
                    message="hello",
                    character=None,
                    metadata={},
                )
            )

        self.assertEqual(
            deps.calls,
            [
                ("reserve", "request-6"),
                ("running", "request-6", "session_loading"),
                ("session", "s-1", 7),
                ("running", "request-6", "runtime_running"),
                ("locked_turn", "request-6", "s-1"),
                ("running", "request-6", "persisting"),
                ("failed", "request-6", "persisting", "ORCHESTRATOR_FAILED", "persist failed"),
            ],
        )


class AITurnHTTPContractTest(unittest.TestCase):
    def test_turn_request_validates_required_request_id_and_message(self):
        from pydantic import ValidationError

        from ai.schemas.turn import AITurnRequest

        request = AITurnRequest(request_id="request-1", message="hello")

        self.assertEqual(request.request_id, "request-1")
        self.assertEqual(request.message, "hello")

        with self.assertRaises(ValidationError):
            AITurnRequest(request_id="short", message="hello")

        with self.assertRaises(ValidationError):
            AITurnRequest(request_id="request-1", message="")

        with self.assertRaises(ValidationError):
            AITurnRequest(request_id="request-1", message="   ")

        with self.assertRaises(ValidationError):
            AITurnRequest(request_id="request-1", message="hello", user_id=7)

    def test_turn_history_response_exposes_pagination_contract(self):
        from ai.schemas.turn import AITurnHistoryItem, AITurnHistoryResponse

        response = AITurnHistoryResponse(
            session_id="s-1",
            items=[
                AITurnHistoryItem(
                    id=1,
                    role="user",
                    content="hello",
                    character="sakura",
                    sequence_no=1,
                    created_at="2026-06-08T12:00:00",
                )
            ],
            has_more=True,
            next_before_sequence_no=1,
        )

        self.assertEqual(response.session_id, "s-1")
        self.assertTrue(response.has_more)
        self.assertEqual(response.next_before_sequence_no, 1)


class AITurnRouterTest(unittest.IsolatedAsyncioTestCase):
    async def test_turn_router_maps_orchestrator_error_to_http_detail(self):
        from unittest.mock import patch

        from fastapi import HTTPException

        from ai.orchestrator.errors import RequestInProgress
        from ai.routers.turn import create_ai_turn
        from ai.schemas.turn import AITurnRequest

        async def raise_in_progress(_command):
            raise RequestInProgress("same request_id is still running")

        with patch("ai.routers.turn.handle_turn", raise_in_progress):
            with self.assertRaises(HTTPException) as error:
                await create_ai_turn(
                    AITurnRequest(request_id="request-7", message="hello"),
                    user_id=7,
                )

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(
            error.exception.detail,
            {
                "error_code": "REQUEST_IN_PROGRESS",
                "message": "same request_id is still running",
            },
        )

    async def test_turn_router_maps_harness_error_to_http_detail(self):
        from unittest.mock import patch

        from fastapi import HTTPException

        from ai.harness.errors import PlannerInvalidAction
        from ai.routers.turn import create_ai_turn
        from ai.schemas.turn import AITurnRequest

        async def raise_planner_error(_command):
            raise PlannerInvalidAction("planner output invalid")

        with patch("ai.routers.turn.handle_turn", raise_planner_error):
            with self.assertRaises(HTTPException) as error:
                await create_ai_turn(
                    AITurnRequest(request_id="request-8", message="hello"),
                    user_id=7,
                )

        self.assertEqual(error.exception.status_code, 502)
        self.assertEqual(
            error.exception.detail,
            {
                "error_code": "PLANNER_INVALID_ACTION",
                "message": "planner output invalid",
            },
        )

    async def test_turn_stream_router_returns_sse_response(self):
        from unittest.mock import AsyncMock, patch

        from fastapi.responses import StreamingResponse

        from ai.routers.turn import create_ai_turn_stream
        from ai.schemas.turn import AITurnRequest
        from ai.orchestrator.schemas import AITurnResult

        async def fake_handle_turn(_command):
            return AITurnResult(
                request_id="request-stream-1",
                session_id="s-1",
                answer="hello stream",
                status="completed",
                trace_id="trace-1",
            )

        with patch("ai.routers.turn.handle_turn", AsyncMock(side_effect=fake_handle_turn)):
            response = await create_ai_turn_stream(
                AITurnRequest(request_id="request-stream-1", message="hello"),
                user_id=7,
            )

            self.assertIsInstance(response, StreamingResponse)
            self.assertEqual(response.media_type, "text/event-stream")

            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk.decode() if isinstance(chunk, bytes) else chunk)

        body = "".join(chunks)
        self.assertIn("event: session", body)
        self.assertIn("data: s-1", body)
        self.assertIn("hello st", body)
        self.assertIn("ream", body)
        self.assertIn("data: [DONE]", body)

    async def test_history_router_uses_authenticated_user_and_repository_page(self):
        from datetime import datetime
        from unittest.mock import AsyncMock, patch

        from ai.models.agent_session import AgentSession
        from ai.models.agent_turn import AgentTurn
        from ai.routers.turn import get_ai_turn_history

        class FakeSessionContext:
            async def __aenter__(self):
                return object()

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        agent_session = AgentSession(session_id="s-1", user_id=7, status="active")
        turns = [
            AgentTurn(
                id=10,
                session_id="s-1",
                user_id=7,
                sequence_no=2,
                role="assistant",
                content="hi",
                character="sakura",
                created_at=datetime(2026, 6, 8, 12, 0, 0),
            )
        ]

        with patch("ai.routers.turn.get_ai_sessionmaker", return_value=lambda: FakeSessionContext()), patch(
            "ai.routers.turn.get_latest_active_session_for_user_character",
            AsyncMock(return_value=agent_session),
        ) as get_session, patch(
            "ai.routers.turn.list_session_turns_for_user",
            AsyncMock(return_value=(turns, True)),
        ) as list_turns:
            response = await get_ai_turn_history(
                character="sakura",
                limit=1,
                before_sequence_no=None,
                user_id=7,
            )

        get_session.assert_awaited_once()
        self.assertEqual(get_session.await_args.kwargs["user_id"], 7)
        self.assertEqual(get_session.await_args.kwargs["character"], "sakura")
        list_turns.assert_awaited_once()
        self.assertEqual(list_turns.await_args.kwargs["user_id"], 7)
        self.assertEqual(response.session_id, "s-1")
        self.assertTrue(response.has_more)
        self.assertEqual(response.next_before_sequence_no, 2)
        self.assertEqual(response.items[0].content, "hi")

    async def test_clear_history_router_hard_deletes_current_user_character(self):
        from unittest.mock import AsyncMock, patch

        from ai.routers.turn import clear_ai_turn_history

        class FakeDB:
            def __init__(self):
                self.commits = 0

            async def commit(self):
                self.commits += 1

        class FakeSessionContext:
            def __init__(self):
                self.db = FakeDB()

            async def __aenter__(self):
                return self.db

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        context = FakeSessionContext()
        with patch("ai.routers.turn.get_ai_sessionmaker", return_value=lambda: context), patch(
            "ai.routers.turn.clear_user_agent_history",
            AsyncMock(return_value=(1, 2)),
        ) as clear_history:
            response = await clear_ai_turn_history(character="rin", user_id=7)

        clear_history.assert_awaited_once()
        self.assertEqual(clear_history.await_args.kwargs["user_id"], 7)
        self.assertEqual(clear_history.await_args.kwargs["character"], "rin")
        self.assertEqual(context.db.commits, 1)
        self.assertEqual(response, {"cleared_sessions": 1, "cleared_turns": 2})


class RepositoryAITurnDependenciesTest(unittest.IsolatedAsyncioTestCase):
    async def test_locked_turn_revalidates_locked_session_active_status(self):
        from unittest.mock import AsyncMock, patch

        from ai.models.agent_session import AgentSession
        from ai.orchestrator.errors import SessionNotActive
        from ai.orchestrator.schemas import AITurnCommand
        from ai.orchestrator.service import RepositoryAITurnDependencies

        class FakeTransaction:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        class FakeDB:
            def begin(self):
                return FakeTransaction()

        class FakeSessionContext:
            async def __aenter__(self):
                return FakeDB()

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        locked_session = AgentSession(
            session_id="s-1",
            user_id=7,
            status="archived",
        )
        dependencies = RepositoryAITurnDependencies(sessionmaker=lambda: FakeSessionContext())

        with patch(
            "ai.orchestrator.service.get_agent_session_for_update",
            AsyncMock(return_value=locked_session),
        ), patch("ai.orchestrator.service.list_recent_turns", AsyncMock()) as list_recent:
            with self.assertRaises(SessionNotActive) as error:
                await dependencies.run_locked_turn(
                    AITurnCommand(
                        request_id="request-8",
                        session_id="s-1",
                        user_id=7,
                        message="hello",
                        character=None,
                        metadata={},
                    ),
                    locked_session,
                    AsyncMock(),
                )

        self.assertEqual(error.exception.error_code, "SESSION_NOT_ACTIVE")
        list_recent.assert_not_called()

    def test_session_ownership_error_uses_documented_error_code(self):
        from ai.orchestrator.errors import SessionOwnershipError

        self.assertEqual(SessionOwnershipError.error_code, "SESSION_OWNERSHIP_ERROR")


class AITurnResponseAssemblyTest(unittest.TestCase):
    def test_assemble_response_preserves_runtime_status(self):
        from ai.orchestrator.responses import assemble_response
        from ai.orchestrator.schemas import AITurnCommand, RunResult

        session = type("Session", (), {"session_id": "s-1"})()

        response = assemble_response(
            AITurnCommand(
                request_id="request-9",
                session_id="s-1",
                user_id=7,
                message="hello",
                character=None,
                metadata={},
            ),
            session,
            RunResult(
                answer="Need approval",
                trace_id="run-1",
                metadata={"status": "waiting_permission"},
            ),
        )

        self.assertEqual(response.status, "waiting_permission")
        self.assertEqual(response.trace_id, "run-1")


if __name__ == "__main__":
    unittest.main()
