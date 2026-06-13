import unittest


class Phase6RoutingBudgetTest(unittest.TestCase):
    def test_budget_builds_degraded_route_policy(self):
        from ai.routing.budget import RunBudget, build_route_policy

        policy = build_route_policy(
            RunBudget(remaining_tokens=1500, remaining_cost_usd=0.50),
            task_type="planner",
        )

        self.assertTrue(policy.compact_context)
        self.assertTrue(policy.allow_fallback)
        self.assertTrue(policy.disable_rerank)

    def test_choose_model_uses_local_route_when_forced(self):
        from ai.config.model_routes import ModelRoute
        from ai.routing.policy import RoutePolicy, choose_model

        def resolver(character, task_type):
            return ModelRoute(provider="deepseek", model="deepseek-chat")

        route = choose_model(
            task_type="planner",
            character=None,
            policy=RoutePolicy(
                force_local=True,
                local_fallback_route=ModelRoute(provider="local", model="local-small"),
            ),
            resolver=resolver,
        )

        self.assertEqual(route.provider, "local")
        self.assertEqual(route.model, "local-small")

    def test_choose_model_uses_fallback_for_unhealthy_provider(self):
        from ai.config.model_routes import ModelRoute
        from ai.routing.policy import RoutePolicy, choose_model

        def resolver(character, task_type):
            return ModelRoute(provider="deepseek", model="deepseek-chat")

        route = choose_model(
            task_type="planner",
            character=None,
            policy=RoutePolicy(
                allow_fallback=True,
                unhealthy_providers=["deepseek"],
                fallback_routes={"planner": ModelRoute(provider="openai", model="gpt-4.1-mini")},
            ),
            resolver=resolver,
        )

        self.assertEqual(route.provider, "openai")


class Phase6HealthCanaryLoadTest(unittest.TestCase):
    def test_provider_health_marks_provider_unhealthy_after_failures(self):
        from ai.ops.health import ProviderHealthTracker

        tracker = ProviderHealthTracker(max_failures=2)
        tracker.record_failure("deepseek")
        tracker.record_failure("deepseek")

        self.assertFalse(tracker.is_healthy("deepseek"))
        self.assertEqual(tracker.snapshot()["deepseek"]["failures"], 2)

    def test_canary_assignment_is_deterministic(self):
        from ai.ops.rollout import is_canary_session

        first = is_canary_session("session-1", percentage=25)
        second = is_canary_session("session-1", percentage=25)

        self.assertEqual(first, second)
        self.assertFalse(is_canary_session("session-1", percentage=0))
        self.assertTrue(is_canary_session("session-1", percentage=100))

    def test_loadtest_scenario_reports_expected_operation_count(self):
        from ai.loadtest.scenarios import LoadTestScenario

        scenario = LoadTestScenario(
            name="mixed_agent_load",
            sessions=10,
            turns_per_session=4,
            expected_cache_hit_ratio=0.3,
        )

        self.assertEqual(scenario.total_turns, 40)
        self.assertEqual(scenario.to_dict()["expected_cache_hit_ratio"], 0.3)


if __name__ == "__main__":
    unittest.main()
