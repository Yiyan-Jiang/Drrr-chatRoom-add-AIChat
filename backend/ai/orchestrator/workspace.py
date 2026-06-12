from ai.models.agent_session import AgentSession
from ai.models.agent_turn import AgentTurn
from ai.orchestrator.schemas import AITurnCommand, TurnWorkspace


def build_workspace(
    command: AITurnCommand,
    session: AgentSession,
    recent_turns: list[AgentTurn],
) -> TurnWorkspace:
    return TurnWorkspace(command=command, session=session, recent_turns=recent_turns)
