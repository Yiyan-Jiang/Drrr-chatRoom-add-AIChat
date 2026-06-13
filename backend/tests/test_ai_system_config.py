import unittest

from pydantic import ValidationError

from ai.config.model_routes import resolve_model_route
from ai.prompts.character_service import (
    DEFAULT_CHARACTER,
    get_allowed_characters,
    get_system_prompt,
    normalize_character,
)
from ai.providers.registry import OpenAICompatibleProvider, get_provider
from ai.schemas.chat import AIChatRequest


class AISystemConfigTest(unittest.TestCase):
    def test_ai_chat_request_lives_in_ai_schema_package(self):
        request = AIChatRequest(message="hello", character="rin")

        self.assertEqual(request.message, "hello")
        self.assertEqual(request.character, "rin")

        with self.assertRaises(ValidationError):
            AIChatRequest(message="")

    def test_character_metadata_and_prompt_are_loaded_from_ai_prompts(self):
        characters = get_allowed_characters()

        self.assertIn("sakura", characters)
        self.assertEqual(DEFAULT_CHARACTER, "sakura")
        self.assertEqual(normalize_character("missing"), "sakura")
        self.assertEqual(normalize_character("rin"), "rin")
        self.assertIn("小樱", get_system_prompt("sakura"))

    def test_model_route_uses_character_and_task_type(self):
        route = resolve_model_route(character="sakura", task_type="chat")

        self.assertEqual(route.provider, "deepseek")
        self.assertEqual(route.model, "deepseek-chat")

    def test_provider_registry_returns_openai_compatible_provider(self):
        provider = get_provider("deepseek")

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.name, "deepseek")

    def test_provider_registry_reports_unknown_provider_and_missing_key(self):
        from unittest.mock import patch

        with self.assertRaisesRegex(ValueError, "Unsupported AI provider: missing"):
            get_provider("missing")

        provider = get_provider("deepseek")
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DEEPSEEK_API_KEY"):
                provider.create_client()


if __name__ == "__main__":
    unittest.main()
