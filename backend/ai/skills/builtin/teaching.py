from ai.skills.manifest import SkillManifest


TEACHING_TOOLS = [
    "generate_learning_path",
    "explain_concept",
    "generate_practice",
    "grade_answer",
    "record_stage_summary",
    "record_review_report",
]

TEACHING_ARTIFACT_CONTRACTS = {
    "learning_path": {"type": "object"},
    "lesson_note": {"type": "object"},
    "practice_record": {"type": "object"},
    "understanding_check": {"type": "object"},
    "stage_summary": {"type": "object"},
    "review_report": {"type": "object"},
}

TEACHING_CHECKPOINT_SCHEMA = {
    "type": "object",
    "required": ["skill", "next_teaching_action"],
    "properties": {
        "skill": {"const": "teaching"},
        "goal": {"type": "string"},
        "level": {"type": "string"},
        "time_budget": {"type": "string"},
        "path_artifact_id": {"type": "string"},
        "current_stage_id": {"type": "string"},
        "current_topic": {"type": "string"},
        "mastered_topics": {"type": "array"},
        "weak_points": {"type": "array"},
        "last_teaching_action": {"type": "string"},
        "next_teaching_action": {"type": "string"},
        "waiting_for": {"type": ["string", "null"]},
    },
}


def create_teaching_manifest() -> SkillManifest:
    return SkillManifest(
        name="teaching",
        version=1,
        description="Structured learning tutor skill with artifacts and checkpointed progress.",
        instruction=(
            "你是学习辅导 skill。必须先识别用户学习目标、基础水平和可用时间。"
            "如果信息不足，先 ask_user。信息足够时调用 generate_learning_path。"
            "教学过程必须围绕 checkpoint 推进，每轮最多推进一个教学动作。"
            "学习路径、讲解笔记、练习记录、理解检查、阶段总结和复盘报告必须写入 artifact。"
            "不能只在最终回答里保存学习状态。"
        ),
        tools=list(TEACHING_TOOLS),
        artifact_contracts=dict(TEACHING_ARTIFACT_CONTRACTS),
        checkpoint_schema=dict(TEACHING_CHECKPOINT_SCHEMA),
        policy={"allow": list(TEACHING_TOOLS)},
    )
