from collections.abc import Awaitable, Callable
from typing import Protocol

from ai.database import get_ai_sessionmaker
from ai.models.agent_session import AgentSession
from ai.orchestrator.errors import (
    OrchestratorError,
    SessionNotActive,
    SessionNotFound,
    SessionOwnershipError,
)
from ai.orchestrator.idempotency import resolve_reservation
from ai.orchestrator.persistence import persist_success
from ai.orchestrator.responses import assemble_response
from ai.orchestrator.runtime import run_fake_harness
from ai.orchestrator.schemas import AITurnCommand, AITurnResult
from ai.orchestrator.sessions import load_or_create_session_for_turn
from ai.orchestrator.workspace import build_workspace
from ai.repositories.agent_audit_repository import (
    RequestReservation,
    mark_audit_failed,
    mark_audit_running,
    reserve_request,
)
from ai.repositories.agent_session_repository import get_agent_session_for_update
from ai.repositories.agent_turn_repository import list_recent_turns
from ai.memory.repositories import list_relevant_memories


class AITurnDependencies(Protocol):
    async def reserve_request(self, command: AITurnCommand) -> RequestReservation:
        ...

    async def mark_running(self, request_id: str, stage: str) -> None:
        ...

    async def mark_failed(
        self,
        request_id: str,
        stage: str,
        error_code: str,
        error_message: str,
    ) -> None:
        ...

    async def load_or_create_session(self, command: AITurnCommand) -> AgentSession:
        ...

    async def run_locked_turn(
        self,
        command: AITurnCommand,
        session: AgentSession,
        mark_stage: Callable[[str], Awaitable[None]],
    ) -> AITurnResult:
        ...


class RepositoryAITurnDependencies:
    def __init__(self, sessionmaker=None):
        self._sessionmaker = sessionmaker or get_ai_sessionmaker()

    async def reserve_request(self, command: AITurnCommand) -> RequestReservation:
        async with self._sessionmaker() as db:
            return await reserve_request(
                db=db,
                request_id=command.request_id,
                user_id=command.user_id,
                session_id=command.session_id,
            )

    async def mark_running(self, request_id: str, stage: str) -> None:
        async with self._sessionmaker() as db:
            await mark_audit_running(db, request_id=request_id, stage=stage)
            await db.commit()

    async def mark_failed(
        self,
        request_id: str,
        stage: str,
        error_code: str,
        error_message: str,
    ) -> None:
        async with self._sessionmaker() as db:
            audit = await mark_audit_failed(
                db=db,
                request_id=request_id,
                error_code=error_code,
                error_message=error_message,
            )
            audit.stage = stage
            await db.commit()

    async def load_or_create_session(self, command: AITurnCommand) -> AgentSession:
        async with self._sessionmaker() as db:
            return await load_or_create_session_for_turn(db, command)

    async def run_locked_turn(
        self,
        command: AITurnCommand,
        session: AgentSession,
        mark_stage: Callable[[str], Awaitable[None]],
    ) -> AITurnResult:
        async with self._sessionmaker() as db:
            async with db.begin():
                locked_session = await get_agent_session_for_update(db, session.session_id)
                if locked_session is None:
                    raise SessionNotFound(f"Session not found: {session.session_id}")
                if locked_session.user_id != command.user_id:
                    raise SessionOwnershipError("session belongs to another user")
                if locked_session.status != "active":
                    raise SessionNotActive(f"Session is not active: {session.session_id}")

                recent_turns = await list_recent_turns(db, locked_session.session_id, limit=20)
                long_term_memories = await list_relevant_memories(
                    db=db,
                    user_id=command.user_id,
                    character=command.character,
                    query=command.message,
                    limit=8,
                )
                workspace = build_workspace(
                    command,
                    locked_session,
                    recent_turns,
                    long_term_memories=long_term_memories,
                )
                run_result = await run_fake_harness(workspace)
                response = assemble_response(command, locked_session, run_result)
                await mark_stage("persisting")
                await persist_success(db, command, locked_session, run_result, response)
                return response


class AITurnOrchestrator:
    def __init__(self, dependencies: AITurnDependencies | None = None):
        self._dependencies = dependencies or RepositoryAITurnDependencies()

    async def handle_turn(self, command: AITurnCommand) -> AITurnResult:
        reservation = await self._dependencies.reserve_request(command)
        cached_result = resolve_reservation(reservation)
        if cached_result is not None:
            return cached_result

        stage = "session_loading"
        try:
            await self._dependencies.mark_running(command.request_id, stage)
            session = await self._dependencies.load_or_create_session(command)

            stage = "runtime_running"
            await self._dependencies.mark_running(command.request_id, stage)

            async def mark_stage(next_stage: str) -> None:
                nonlocal stage
                stage = next_stage
                await self._dependencies.mark_running(command.request_id, next_stage)

            return await self._dependencies.run_locked_turn(command, session, mark_stage)
        except Exception as exc:
            error_code = (
                exc.error_code if isinstance(exc, OrchestratorError) else "ORCHESTRATOR_FAILED"
            )
            await self._dependencies.mark_failed(
                command.request_id,
                stage,
                error_code,
                str(exc),
            )
            raise


async def handle_turn(command: AITurnCommand) -> AITurnResult:
    return await AITurnOrchestrator().handle_turn(command)
