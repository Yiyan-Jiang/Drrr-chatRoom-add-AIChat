import json

from ai.harness.context import CompiledContext
from ai.harness.planner_schema import get_llm_planner_action_schema


def build_planner_contract_prompt() -> str:
    return (
        "You are the planner for this agent runtime. Return exactly one JSON object "
        "and no markdown or prose. The JSON object must include a top-level string "
        '"type" field. Valid action schemas are:\n'
        f"{json.dumps(get_llm_planner_action_schema(), ensure_ascii=False, sort_keys=True)}\n"
        'For a direct chat reply, use exactly: {"type":"answer","answer":"your reply"}.'
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
