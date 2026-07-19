from ai.models.agent_memory import AgentMemory
from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn
from ai.orchestrator.schemas import AITurnCommand, TurnWorkspace


def build_workspace(
    command: AITurnCommand,
    session: AgentSession,
    recent_turns: list[AgentTurn],
    long_term_memories: list[AgentMemory] | None = None,
) -> TurnWorkspace:
    return TurnWorkspace(
        command=command,
        session=session,
        recent_turns=recent_turns,
        long_term_memories=long_term_memories or [],
    )
