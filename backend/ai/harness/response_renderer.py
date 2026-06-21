from ai.prompts.character_service import get_system_prompt, normalize_character


class FinalResponseRenderer:
    def __init__(self, gateway):
        self._gateway = gateway

    async def render(self, *, character: str | None, draft_text: str) -> str:
        actual_character = normalize_character(character)
        result = await self._gateway.complete(
            [
                {"role": "system", "content": get_system_prompt(actual_character)},
                {
                    "role": "user",
                    "content": (
                        "请以该角色的语气，把下面的草稿改写成最终面向用户的回复。"
                        "保持原意不变，不要添加任何 markdown。\n"
                        f"{draft_text}"
                    ),
                },
            ],
            response_format=None,
        )
        return result.raw_text
