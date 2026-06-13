from ai.memory.models import AgentMemoryItem, ConversationSummary


def refresh_summary(
    previous: ConversationSummary,
    turns: list,
) -> ConversationSummary:
    new_turns = [
        turn for turn in turns if turn.sequence_no > previous.source_last_sequence_no
    ]
    if not new_turns:
        return previous

    text = " ".join([previous.text] + [turn.content for turn in new_turns]).strip()
    return ConversationSummary(
        session_id=previous.session_id,
        text=text,
        source_last_sequence_no=max(turn.sequence_no for turn in new_turns),
    )


def extract_memory_for_turn(
    user_id: str,
    session_id: str,
    turn,
) -> list[AgentMemoryItem]:
    if turn.role != "user":
        return []
    if "喜欢" not in turn.content and "偏好" not in turn.content:
        return []
    return [
        AgentMemoryItem(
            user_id=user_id,
            session_id=session_id,
            memory_type="user_preference",
            content=turn.content,
            source_sequence_no=turn.sequence_no,
        )
    ]
