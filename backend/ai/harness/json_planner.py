import json

from ai.harness.context import CompiledContext
from ai.harness.planner_schema import get_llm_planner_action_schema


def build_planner_contract_prompt() -> str:
    return (
        "你是这个 agent 运行时的规划器（planner）。只返回一个 JSON 对象，"
        "不要输出任何 markdown 或解释性文字。该 JSON 对象必须包含顶层字符串字段 "
        '"type"。可用的 action schema 如下：\n'
        f"{json.dumps(get_llm_planner_action_schema(), ensure_ascii=False, sort_keys=True)}\n"
        '若要直接进行对话回复，请严格使用：{"type":"answer","answer":"你的回复"}。'
    )


class JSONPlannerClient:
    def __init__(self, gateway):
        self._gateway = gateway

    async def plan(self, context: CompiledContext) -> str:
        result = await self._gateway.complete(
            [
                {"role": "system", "content": build_planner_contract_prompt()},
                *context.messages,
            ]
        )
        return result.raw_text
