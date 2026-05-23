import os
from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass(frozen=True)
class OpenAICompatibleProvider:
    name: str
    api_key_env: str
    default_base_url: str
    base_url_env: str | None = None

    def create_client(self) -> AsyncOpenAI:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"{self.api_key_env} is not set")
        base_url = (
            os.environ.get(self.base_url_env)
            if self.base_url_env
            else self.default_base_url
        )
        return AsyncOpenAI(api_key=api_key, base_url=base_url or self.default_base_url)


_PROVIDERS = {
    "deepseek": OpenAICompatibleProvider(
        name="deepseek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        default_base_url="https://api.deepseek.com",
    ),
    "openai": OpenAICompatibleProvider(
        name="openai",
        api_key_env="OPENAI_API_KEY",
        default_base_url="https://api.openai.com/v1",
    ),
    "local": OpenAICompatibleProvider(
        name="local",
        api_key_env="LOCAL_OPENAI_API_KEY",
        base_url_env="LOCAL_OPENAI_BASE_URL",
        default_base_url="http://127.0.0.1:8001/v1",
    ),
}


def get_provider(name: str) -> OpenAICompatibleProvider:
    try:
        return _PROVIDERS[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported AI provider: {name}") from exc
