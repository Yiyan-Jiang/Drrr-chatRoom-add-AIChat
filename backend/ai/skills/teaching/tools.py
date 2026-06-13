from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolExecutionContext, ToolPermission, ToolSpec


LEVELS = {"beginner", "intermediate", "advanced", "unknown"}
NEXT_ACTIONS = {
    "ask_user",
    "generate_path",
    "explain",
    "practice",
    "grade",
    "remediate",
    "advance",
    "summarize",
}


def _require_mapping(arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    return dict(arguments)


def _require_text(arguments: dict, key: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value.strip()


def _list_value(arguments: dict, key: str) -> list:
    value = arguments.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _checkpoint(run) -> dict:
    checkpoint = getattr(run, "checkpoint_payload", None)
    if isinstance(checkpoint, dict):
        return dict(checkpoint)
    return {
        "skill": "teaching",
        "mastered_topics": [],
        "weak_points": [],
        "next_teaching_action": "generate_path",
        "waiting_for": None,
    }


async def _write_artifact(context: ToolExecutionContext, artifact_type: str, payload: dict):
    if context.repository is None or context.run is None:
        raise RuntimeError("teaching repository is not available")
    return await context.repository.write_artifact(context.run, artifact_type, payload)


async def _update_checkpoint(context: ToolExecutionContext, checkpoint: dict) -> None:
    if context.repository is None or context.run is None:
        raise RuntimeError("teaching repository is not available")
    await context.repository.update_checkpoint(context.run, checkpoint)


def _normalize_learning_path(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    level = normalized.get("level", "unknown")
    if level not in LEVELS:
        raise ValueError("level must be beginner, intermediate, advanced, or unknown")
    return {
        "goal": _require_text(normalized, "goal"),
        "level": level,
        "time_budget": _require_text(normalized, "time_budget"),
        "constraints": _list_value(normalized, "constraints"),
    }


async def _generate_learning_path(
    context: ToolExecutionContext,
    arguments: dict,
) -> ToolResult:
    goal = arguments["goal"]
    stages = [
        {
            "stage_id": "stage-1",
            "title": "建立基础模型",
            "objective": f"理解 {goal} 的核心概念",
            "topics": ["核心概念", "基本术语"],
            "practice": "short_answer",
            "success_criteria": ["能用自己的话解释核心概念"],
        },
        {
            "stage_id": "stage-2",
            "title": "动手练习",
            "objective": f"完成一个 {goal} 的小任务",
            "topics": ["步骤拆解", "常见错误"],
            "practice": "mini_task",
            "success_criteria": ["能独立完成一个小练习"],
        },
        {
            "stage_id": "stage-3",
            "title": "复盘迁移",
            "objective": "总结方法并迁移到新问题",
            "topics": ["复盘", "迁移应用"],
            "practice": "explain_back",
            "success_criteria": ["能说明适用边界和下一步计划"],
        },
    ]
    payload = {
        "goal": goal,
        "level": arguments["level"],
        "time_budget": arguments["time_budget"],
        "stages": stages,
    }
    artifact = await _write_artifact(context, "learning_path", payload)
    checkpoint = _checkpoint(context.run)
    checkpoint.update(
        {
            "skill": "teaching",
            "goal": goal,
            "level": arguments["level"],
            "time_budget": arguments["time_budget"],
            "path_artifact_id": getattr(artifact, "artifact_id", "learning_path"),
            "current_stage_id": "stage-1",
            "current_topic": stages[0]["topics"][0],
            "mastered_topics": checkpoint.get("mastered_topics") or [],
            "weak_points": checkpoint.get("weak_points") or [],
            "last_teaching_action": "generate_path",
            "next_teaching_action": "explain",
            "waiting_for": None,
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="generate_learning_path",
        call_id=context.call_id,
        ok=True,
        result_kind="learning_path",
        preview=f"{goal}: {len(stages)} stages",
        payload=payload,
    )


def _normalize_explain(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    return {
        "stage_id": _require_text(normalized, "stage_id"),
        "topic": _require_text(normalized, "topic"),
        "level": normalized.get("level", "unknown"),
        "style": normalized.get("style", "simple"),
    }


async def _explain_concept(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    topic = arguments["topic"]
    payload = {
        "stage_id": arguments["stage_id"],
        "topic": topic,
        "summary": f"{topic} 的关键是先理解它解决什么问题，再看基本流程。",
        "examples": [f"用一个简单例子观察 {topic} 的输入、处理和输出。"],
        "misconceptions": [f"不要把 {topic} 当成孤立结论，先关注适用场景。"],
    }
    await _write_artifact(context, "lesson_note", payload)
    checkpoint = _checkpoint(context.run)
    checkpoint.update(
        {
            "skill": "teaching",
            "current_stage_id": arguments["stage_id"],
            "current_topic": topic,
            "last_teaching_action": "explain",
            "next_teaching_action": "practice",
            "waiting_for": None,
            "mastered_topics": checkpoint.get("mastered_topics") or [],
            "weak_points": checkpoint.get("weak_points") or [],
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="explain_concept",
        call_id=context.call_id,
        ok=True,
        result_kind="lesson_note",
        preview=payload["summary"],
        payload=payload,
    )


def _normalize_practice(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    return {
        "stage_id": _require_text(normalized, "stage_id"),
        "topic": _require_text(normalized, "topic"),
        "difficulty": normalized.get("difficulty", "normal"),
        "practice_type": normalized.get("practice_type", "short_answer"),
    }


async def _generate_practice(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    question = f"请用自己的话解释：{arguments['topic']} 解决了什么问题？"
    payload = {
        "stage_id": arguments["stage_id"],
        "check_type": arguments["practice_type"],
        "prompt": question,
        "user_response": "",
        "assessment": "pending",
        "next_action": "grade",
    }
    await _write_artifact(context, "understanding_check", payload)
    checkpoint = _checkpoint(context.run)
    checkpoint.update(
        {
            "skill": "teaching",
            "current_stage_id": arguments["stage_id"],
            "current_topic": arguments["topic"],
            "current_practice": {
                "question": question,
                "expected_answer": f"{arguments['topic']} 的作用和基本机制",
            },
            "last_teaching_action": "practice",
            "next_teaching_action": "grade",
            "waiting_for": "user_answer",
            "mastered_topics": checkpoint.get("mastered_topics") or [],
            "weak_points": checkpoint.get("weak_points") or [],
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="generate_practice",
        call_id=context.call_id,
        ok=True,
        result_kind="understanding_check",
        preview=question,
        payload=payload,
    )


def _normalize_grade(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    return {
        "stage_id": _require_text(normalized, "stage_id"),
        "question": _require_text(normalized, "question"),
        "expected_answer": _require_text(normalized, "expected_answer"),
        "user_answer": _require_text(normalized, "user_answer"),
    }


def _grade(expected: str, answer: str) -> str:
    normalized_answer = answer.strip().lower()
    if normalized_answer in {"不知道", "不会", "不清楚", "no idea"}:
        return "incorrect"
    expected_tokens = [token for token in expected.lower().split() if token]
    if expected_tokens and all(token in normalized_answer for token in expected_tokens[:2]):
        return "correct"
    if len(normalized_answer) >= 8:
        return "partial"
    return "incorrect"


async def _grade_answer(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    result = _grade(arguments["expected_answer"], arguments["user_answer"])
    weak_points = [] if result == "correct" else [arguments["question"]]
    payload = {
        "stage_id": arguments["stage_id"],
        "question": arguments["question"],
        "expected_answer": arguments["expected_answer"],
        "user_answer": arguments["user_answer"],
        "result": result,
        "feedback": "回答方向正确。" if result == "correct" else "需要补充关键概念后再练习。",
        "weak_points": weak_points,
    }
    await _write_artifact(context, "practice_record", payload)
    if result != "correct":
        await _write_artifact(
            context,
            "understanding_check",
            {
                "stage_id": arguments["stage_id"],
                "check_type": "remediate",
                "prompt": arguments["question"],
                "user_response": arguments["user_answer"],
                "assessment": result,
                "next_action": "remediate",
            },
        )
    checkpoint = _checkpoint(context.run)
    mastered = set(checkpoint.get("mastered_topics") or [])
    weak = set(checkpoint.get("weak_points") or [])
    if result == "correct":
        mastered.add(arguments["question"])
        next_action = "advance"
    else:
        weak.update(weak_points)
        next_action = "remediate"
    checkpoint.update(
        {
            "skill": "teaching",
            "current_stage_id": arguments["stage_id"],
            "mastered_topics": sorted(mastered),
            "weak_points": sorted(weak),
            "last_teaching_action": "grade",
            "next_teaching_action": next_action,
            "waiting_for": None,
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="grade_answer",
        call_id=context.call_id,
        ok=True,
        result_kind="practice_record",
        preview=payload["feedback"],
        payload=payload,
    )


def _normalize_stage_summary(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    return {
        "stage_id": _require_text(normalized, "stage_id"),
        "completed_objectives": _list_value(normalized, "completed_objectives"),
        "mastered_topics": _list_value(normalized, "mastered_topics"),
        "weak_points": _list_value(normalized, "weak_points"),
        "recommended_review": _list_value(normalized, "recommended_review"),
        "next_stage_id": normalized.get("next_stage_id"),
    }


async def _record_stage_summary(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    payload = {
        "stage_id": arguments["stage_id"],
        "completed_objectives": arguments["completed_objectives"],
        "mastered_topics": arguments["mastered_topics"],
        "weak_points": arguments["weak_points"],
        "recommended_review": arguments["recommended_review"],
        "next_stage_id": arguments["next_stage_id"],
    }
    await _write_artifact(context, "stage_summary", payload)
    checkpoint = _checkpoint(context.run)
    checkpoint.update(
        {
            "skill": "teaching",
            "current_stage_id": arguments["next_stage_id"] or arguments["stage_id"],
            "mastered_topics": arguments["mastered_topics"],
            "weak_points": arguments["weak_points"],
            "last_teaching_action": "summarize",
            "next_teaching_action": "explain" if arguments["next_stage_id"] else "summarize",
            "waiting_for": None,
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="record_stage_summary",
        call_id=context.call_id,
        ok=True,
        result_kind="stage_summary",
        preview=f"stage summarized: {arguments['stage_id']}",
        payload=payload,
    )


def _normalize_review(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    return {
        "goal": _require_text(normalized, "goal"),
        "completed_stages": _list_value(normalized, "completed_stages"),
        "mastery_summary": _require_text(normalized, "mastery_summary"),
        "remaining_gaps": _list_value(normalized, "remaining_gaps"),
        "next_plan": _list_value(normalized, "next_plan"),
    }


async def _record_review_report(context: ToolExecutionContext, arguments: dict) -> ToolResult:
    payload = dict(arguments)
    await _write_artifact(context, "review_report", payload)
    checkpoint = _checkpoint(context.run)
    checkpoint.update(
        {
            "skill": "teaching",
            "goal": arguments["goal"],
            "last_teaching_action": "review",
            "next_teaching_action": "summarize",
            "waiting_for": None,
        }
    )
    await _update_checkpoint(context, checkpoint)
    return ToolResult(
        tool_name="record_review_report",
        call_id=context.call_id,
        ok=True,
        result_kind="review_report",
        preview=arguments["mastery_summary"],
        payload=payload,
    )


def _spec(name: str, description: str, normalize, execute) -> ToolSpec:
    return ToolSpec(
        name=name,
        description=description,
        input_schema={"type": "object"},
        permission=ToolPermission(scope="teaching"),
        normalize=normalize,
        execute=execute,
    )


def register_teaching_tools(registry) -> None:
    registry.register(
        _spec("generate_learning_path", "Generate a staged learning path.", _normalize_learning_path, _generate_learning_path)
    )
    registry.register(
        _spec("explain_concept", "Write a lesson note for a concept.", _normalize_explain, _explain_concept)
    )
    registry.register(
        _spec("generate_practice", "Generate a practice or understanding check.", _normalize_practice, _generate_practice)
    )
    registry.register(
        _spec("grade_answer", "Grade a user answer and update learning state.", _normalize_grade, _grade_answer)
    )
    registry.register(
        _spec("record_stage_summary", "Record a stage summary and advance checkpoint.", _normalize_stage_summary, _record_stage_summary)
    )
    registry.register(
        _spec("record_review_report", "Record a final learning review report.", _normalize_review, _record_review_report)
    )
