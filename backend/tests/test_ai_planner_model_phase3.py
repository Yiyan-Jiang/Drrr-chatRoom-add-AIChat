import unittest
from types import SimpleNamespace
from unittest.mock import patch


class Phase3PlannerModelConfigTest(unittest.TestCase):
    def test_model_config_requires_api_key_and_model(self):
        from ai.harness.model_config import PlannerModelConfigError, load_planner_model_config

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(PlannerModelConfigError) as caught:
                load_planner_model_config()

        self.assertIn("DEEPSEEK_API_KEY", str(caught.exception))

    def test_model_config_falls_back_to_existing_deepseek_environment(self):
        from ai.harness.model_config import load_planner_model_config

        with patch.dict(
            "os.environ",
            {
                "DEEPSEEK_API_KEY": "deepseek-key",
                "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
            },
            clear=True,
        ):
            config = load_planner_model_config()

        self.assertEqual(config.api_key, "deepseek-key")
        self.assertEqual(config.base_url, "https://api.deepseek.com")
        self.assertEqual(config.model, "deepseek-chat")

    def test_model_config_reads_planner_environment(self):
        from ai.harness.model_config import load_planner_model_config

        with patch.dict(
            "os.environ",
            {
                "AGENT_CORE_MODEL_API_KEY": "key",
                "AGENT_CORE_MODEL_BASE_URL": "http://model.test/v1",
                "AGENT_CORE_PLANNER_MODEL": "planner-model",
                "AGENT_CORE_PLANNER_MAX_TOKENS": "512",
                "AGENT_CORE_PLANNER_TIMEOUT_SECONDS": "15",
            },
            clear=True,
        ):
            config = load_planner_model_config()

        self.assertEqual(config.api_key, "key")
        self.assertEqual(config.base_url, "http://model.test/v1")
        self.assertEqual(config.model, "planner-model")
        self.assertEqual(config.max_tokens, 512)
        self.assertEqual(config.timeout_seconds, 15.0)


class Phase3ModelGatewayTest(unittest.IsolatedAsyncioTestCase):
    async def test_gateway_returns_raw_model_text_and_metadata(self):
        from ai.harness.model_config import PlannerModelConfig
        from ai.harness.model_gateway import ModelGateway

        class FakeCompletions:
            async def create(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content='{"type": "answer", "answer": "ok"}'
                            ),
                            finish_reason="stop",
                        )
                    ]
                )

        completions = FakeCompletions()
        fake_client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        gateway = ModelGateway(
            PlannerModelConfig(
                api_key="key",
                base_url="http://model.test/v1",
                model="planner-model",
                max_tokens=256,
                timeout_seconds=10.0,
            ),
            client=fake_client,
        )

        result = await gateway.complete([{"role": "user", "content": "hi"}])

        self.assertEqual(result.raw_text, '{"type": "answer", "answer": "ok"}')
        self.assertEqual(result.model, "planner-model")
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(completions.kwargs["model"], "planner-model")
        self.assertEqual(completions.kwargs["response_format"], {"type": "json_object"})

    async def test_gateway_fails_on_empty_model_content(self):
        from ai.harness.errors import ModelGatewayError
        from ai.harness.model_config import PlannerModelConfig
        from ai.harness.model_gateway import ModelGateway

        class FakeCompletions:
            async def create(self, **_kwargs):
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content=""),
                            finish_reason="stop",
                        )
                    ]
                )

        fake_client = SimpleNamespace(
            chat=SimpleNamespace(completions=FakeCompletions())
        )
        gateway = ModelGateway(
            PlannerModelConfig(
                api_key="key",
                base_url=None,
                model="planner-model",
                max_tokens=256,
                timeout_seconds=10.0,
            ),
            client=fake_client,
        )

        with self.assertRaises(ModelGatewayError):
            await gateway.complete([{"role": "user", "content": "hi"}])


class Phase3JSONPlannerClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_json_planner_client_returns_raw_gateway_output(self):
        from ai.harness.context import CompiledContext
        from ai.harness.json_planner import JSONPlannerClient

        class FakeGateway:
            def __init__(self):
                self.messages = None

            async def complete(self, messages):
                self.messages = messages
                return SimpleNamespace(raw_text="not json")

        gateway = FakeGateway()
        planner = JSONPlannerClient(gateway=gateway)
        context = CompiledContext(
            messages=[{"role": "user", "content": "hello"}],
            ledger=[],
            token_estimate=0,
        )

        raw = await planner.plan(context)

        self.assertEqual(raw, "not json")
        self.assertEqual(gateway.messages[-1], {"role": "user", "content": "hello"})

    async def test_json_planner_client_prepends_action_contract_prompt(self):
        from ai.harness.context import CompiledContext
        from ai.harness.json_planner import JSONPlannerClient

        class FakeGateway:
            def __init__(self):
                self.messages = None

            async def complete(self, messages):
                self.messages = messages
                return SimpleNamespace(raw_text='{"type": "answer", "answer": "ok"}')

        gateway = FakeGateway()
        planner = JSONPlannerClient(gateway=gateway)
        context = CompiledContext(
            messages=[{"role": "user", "content": "hello"}],
            ledger=[],
            token_estimate=0,
        )

        await planner.plan(context)

        self.assertEqual(gateway.messages[0]["role"], "system")
        self.assertIn('"type"', gateway.messages[0]["content"])
        self.assertIn('"answer"', gateway.messages[0]["content"])
        self.assertIn('"tool_calls"', gateway.messages[0]["content"])


if __name__ == "__main__":
    unittest.main()
