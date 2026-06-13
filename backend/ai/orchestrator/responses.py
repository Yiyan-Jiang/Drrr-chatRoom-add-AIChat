from ai.models.agent_session import AgentSession
from ai.orchestrator.schemas import AITurnCommand, AITurnResult, RunResult


def assemble_response(
    command: AITurnCommand,
    session: AgentSession,
    run_result: RunResult,
) -> AITurnResult:
    return AITurnResult(
        request_id=command.request_id,
        session_id=session.session_id,
        answer=run_result.answer,
        status=run_result.metadata.get("status", "completed"),
        trace_id=run_result.trace_id,
    )
