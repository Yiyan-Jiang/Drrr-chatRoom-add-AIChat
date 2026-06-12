import unittest


class Phase7PolicyEngineTest(unittest.TestCase):
    def test_effective_policy_uses_deny_then_ask_precedence_and_trace(self):
        from ai.governance.policy import PolicyLayer, build_effective_policy

        effective = build_effective_policy(
            PolicyLayer(
                policy_id="global",
                version=1,
                layer="global",
                allowed_tools={"search_knowledge", "delete_resource"},
                denied_tools={"delete_resource"},
            ),
            PolicyLayer(
                policy_id="workspace",
                version=2,
                layer="workspace",
                allowed_tools={"delete_resource", "open_resource"},
                ask_tools={"open_resource"},
            ),
        )

        self.assertEqual(effective.tool_decision("delete_resource"), "deny")
        self.assertEqual(effective.tool_decision("open_resource"), "ask")
        self.assertEqual(effective.tool_decision("search_knowledge"), "allow")
        self.assertEqual(
            effective.trace_for("tool.delete_resource")["source_policy_id"],
            "global",
        )

    def test_policy_simulation_resolves_skill_and_tool_decision(self):
        from ai.governance.policy import PolicyLayer
        from ai.governance.simulation import simulate_policy
        from ai.governance.skills import SkillRegistry, SkillRelease, SkillVersion

        registry = SkillRegistry()
        registry.add_version(
            SkillVersion(
                skill_name="knowledge-qa",
                version=1,
                tools={"search_knowledge"},
                artifact_contracts={"response_refs"},
                default=True,
            )
        )
        registry.add_release(
            SkillRelease(
                skill_name="knowledge-qa",
                version=1,
                scope="global",
                percentage=100,
            )
        )

        result = simulate_policy(
            policies=[
                PolicyLayer(
                    policy_id="global",
                    version=1,
                    layer="global",
                    allowed_tools={"search_knowledge"},
                )
            ],
            skill_registry=registry,
            requested_skill="knowledge-qa",
            user_id=7,
            workspace_id=None,
            tool_name="search_knowledge",
        )

        self.assertEqual(result.decision, "allow")
        self.assertEqual(result.skill_version, 1)
        self.assertEqual(result.effective_policy["tools"]["search_knowledge"], "allow")


class Phase7SkillRegistryTest(unittest.TestCase):
    def test_skill_contract_rejects_unknown_tools_and_missing_evidence_artifact(self):
        from ai.governance.skills import (
            SkillContractError,
            SkillVersion,
            validate_skill_contract,
        )

        with self.assertRaises(SkillContractError):
            validate_skill_contract(
                SkillVersion(
                    skill_name="bad",
                    version=1,
                    tools={"unknown_tool"},
                    artifact_contracts={"response_refs"},
                ),
                known_tools={"search_knowledge"},
                known_artifacts={"response_refs"},
            )

        with self.assertRaises(SkillContractError):
            validate_skill_contract(
                SkillVersion(
                    skill_name="evidence",
                    version=1,
                    tools={"search_knowledge"},
                    artifact_contracts=set(),
                    requires_evidence=True,
                ),
                known_tools={"search_knowledge"},
                known_artifacts={"response_refs"},
            )

    def test_skill_release_prefers_specific_scope_then_stable_canary(self):
        from ai.governance.skills import SkillRegistry, SkillRelease, SkillVersion

        registry = SkillRegistry()
        registry.add_version(SkillVersion("assistant", 1, default=True))
        registry.add_version(SkillVersion("assistant", 2))
        registry.add_release(
            SkillRelease(
                skill_name="assistant",
                version=2,
                scope="workspace",
                workspace_id="workspace-1",
                percentage=100,
            )
        )

        selected = registry.resolve_for_run(
            "assistant",
            user_id=3,
            workspace_id="workspace-1",
        )

        self.assertEqual(selected.version, 2)
        self.assertEqual(
            registry.resolve_for_run("assistant", user_id=3, workspace_id=None).version,
            1,
        )


class Phase7RouteGovernanceTest(unittest.TestCase):
    def test_route_governance_returns_explainable_decision_with_fallback(self):
        from ai.governance.routes import (
            GovernedRoute,
            RouteSet,
            select_model_route,
        )
        from ai.routing.budget import RunBudget

        decision = select_model_route(
            task_type="planner",
            character=None,
            user_id=9,
            workspace_id=None,
            budget=RunBudget(remaining_tokens=5000, remaining_cost_usd=0.50),
            route_set=RouteSet(
                route_set_id="default",
                routes=[
                    GovernedRoute(
                        rule_id="rule-primary",
                        task_type="planner",
                        provider="deepseek",
                        model="deepseek-chat",
                    )
                ],
                fallback_routes=[
                    GovernedRoute(
                        rule_id="rule-fallback",
                        task_type="planner",
                        provider="openai",
                        model="gpt-4.1-mini",
                    )
                ],
            ),
            unhealthy_providers={"deepseek"},
        )

        self.assertTrue(decision.fallback)
        self.assertEqual(decision.provider, "openai")
        self.assertEqual(decision.to_event()["event_type"], "model_route_decision")
        self.assertEqual(decision.to_event()["payload"]["rule_id"], "rule-fallback")


class Phase7AdminSloTest(unittest.TestCase):
    def test_change_request_requires_approval_and_records_before_after(self):
        from ai.governance.admin import (
            ChangeNotApproved,
            ChangeRequest,
            apply_change_request,
        )

        change = ChangeRequest(
            change_id="change-1",
            target_type="policy",
            target_id="policy-global",
            patch={"budget": {"max_tokens": 2000}},
        )

        with self.assertRaises(ChangeNotApproved):
            apply_change_request(change, before={"budget": {"max_tokens": 1000}})

        change.approve(operator_id=1)
        result = apply_change_request(change, before={"budget": {"max_tokens": 1000}})

        self.assertEqual(result.status, "applied")
        self.assertEqual(result.audit_log["before"]["budget"]["max_tokens"], 1000)
        self.assertEqual(result.audit_log["after"]["budget"]["max_tokens"], 2000)

    def test_slo_monitor_pauses_and_rolls_back_bad_release(self):
        from ai.governance.slo import ReleaseSlo, RolloutMetrics, evaluate_rollout

        result = evaluate_rollout(
            release_id="release-1",
            slo=ReleaseSlo(max_error_rate=0.01, max_invalid_action_rate=0.02),
            metrics=RolloutMetrics(error_rate=0.03, planner_invalid_action_rate=0.0),
        )

        self.assertEqual(result.action, "rollback")
        self.assertIn("error_rate", result.reason)


if __name__ == "__main__":
    unittest.main()
