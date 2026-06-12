from dataclasses import dataclass
from time import monotonic

from ai.harness.errors import ModelGatewayError
from ai.harness.model_config import PlannerModelConfig


@dataclass(frozen=True)
class ModelGatewayResult:
    raw_text: str
    model: str
    finish_reason: str | None
    elapsed_ms: int


class ModelGateway:
    def __init__(self, config: PlannerModelConfig, client=None):
        self._config = config
        self._client = client or self._create_client(config)

    async def complete(self, messages: list[dict[str, str]]) -> ModelGatewayResult:
        started = monotonic()
        try:
            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                max_tokens=self._config.max_tokens,
                timeout=self._config.timeout_seconds,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise ModelGatewayError(str(exc)) from exc

        choice = _first_choice(response)
        content = getattr(getattr(choice, "message", None), "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ModelGatewayError("model returned empty content")

        return ModelGatewayResult(
            raw_text=content,
            model=self._config.model,
            finish_reason=getattr(choice, "finish_reason", None),
            elapsed_ms=int((monotonic() - started) * 1000),
        )

    def _create_client(self, config: PlannerModelConfig):
        from openai import AsyncOpenAI

        kwargs = {"api_key": config.api_key}
        if config.base_url:
            kwargs["base_url"] = config.base_url
        return AsyncOpenAI(**kwargs)


def _first_choice(response):
    choices = getattr(response, "choices", None)
    if not choices:
        raise ModelGatewayError("model returned no choices")
    return choices[0]
