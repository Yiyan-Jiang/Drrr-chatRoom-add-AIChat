import unittest
from datetime import datetime
from pathlib import Path


class FakeSession:
    def __init__(self):
        self.records = []
        self.flushes = 0

    def add(self, record):
        self.records.append(record)

    async def flush(self):
        self.flushes += 1


class Phase7GovernanceDatabaseTest(unittest.TestCase):
    def test_governance_models_use_expected_table_names(self):
        from ai.models.governance_state import (
            AdminAuditLog,
            AdminChangeApproval,
            AdminChangeRequest,
            AgentPolicyVersion,
            AgentSkill,
            AgentSkillAuditLog,
            AgentSkillRelease,
            AgentSkillVersion,
            ModelRouteAuditLog,
            ModelRouteRelease,
            ModelRouteRule,
            ModelRouteSet,
            ProviderHealthSnapshot,
        )

        self.assertEqual(AgentPolicyVersion.__tablename__, "agent_policy_versions")
        self.assertEqual(AgentSkill.__tablename__, "agent_skills")
        self.assertEqual(AgentSkillVersion.__tablename__, "agent_skill_versions")
        self.assertEqual(AgentSkillRelease.__tablename__, "agent_skill_releases")
        self.assertEqual(AgentSkillAuditLog.__tablename__, "agent_skill_audit_logs")
        self.assertEqual(ModelRouteSet.__tablename__, "model_route_sets")
        self.assertEqual(ModelRouteRule.__tablename__, "model_route_rules")
        self.assertEqual(ModelRouteRelease.__tablename__, "model_route_releases")
        self.assertEqual(ModelRouteAuditLog.__tablename__, "model_route_audit_logs")
        self.assertEqual(ProviderHealthSnapshot.__tablename__, "provider_health_snapshots")
        self.assertEqual(AdminChangeRequest.__tablename__, "admin_change_requests")
        self.assertEqual(AdminChangeApproval.__tablename__, "admin_change_approvals")
        self.assertEqual(AdminAuditLog.__tablename__, "admin_audit_logs")

        self.assertIn("policy_id", AgentPolicyVersion.__table__.c)
        self.assertIn("contract_payload", AgentSkillVersion.__table__.c)
        self.assertIn("percentage", AgentSkillRelease.__table__.c)
        self.assertIn("rule_id", ModelRouteRule.__table__.c)
        self.assertIn("status", AdminChangeRequest.__table__.c)

    def test_governance_migration_creates_baseline_tables(self):
        root = Path(__file__).resolve().parents[1]
        migration = root / "ai" / "alembic" / "versions" / "0004_create_governance_baseline.py"

        text = migration.read_text(encoding="utf-8")

        self.assertIn('revision: str = "0004_create_governance_baseline"', text)
        self.assertIn('down_revision: Union[str, None] = "0003_create_knowledge_baseline"', text)
        self.assertIn('"agent_policy_versions"', text)
        self.assertIn('"agent_skill_versions"', text)
        self.assertIn('"model_route_rules"', text)
        self.assertIn('"admin_change_requests"', text)
        self.assertIn('"provider_health_snapshots"', text)


class Phase7GovernanceRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_governance_records_flush_without_commit(self):
        from ai.governance.repositories import (
            create_admin_change_request,
            create_policy_version,
            create_skill_release,
            create_skill_version,
        )

        session = FakeSession()
        now = datetime(2026, 5, 26, 12, 0, 0)

        policy = await create_policy_version(
            session,
            policy_id="policy-global",
            version=1,
            layer="global",
            payload={"allowed_tools": ["search_knowledge"]},
            created_by=1,
            now=now,
        )
        skill_version = await create_skill_version(
            session,
            skill_name="knowledge-qa",
            version=1,
            instruction="answer with evidence",
            tools=["search_knowledge"],
            artifact_contracts=["response_refs"],
            policy_payload={"requires_evidence": True},
            now=now,
        )
        release = await create_skill_release(
            session,
            release_id="release-1",
            skill_name="knowledge-qa",
            version=1,
            scope="global",
            percentage=25,
            now=now,
        )
        change = await create_admin_change_request(
            session,
            change_id="change-1",
            target_type="policy",
            target_id=policy.policy_id,
            patch={"budget": {"max_tokens": 2000}},
            requested_by=1,
            now=now,
        )

        self.assertEqual(policy.status, "active")
        self.assertEqual(skill_version.contract_payload["tools"], ["search_knowledge"])
        self.assertEqual(release.status, "active")
        self.assertEqual(change.status, "draft")
        self.assertEqual(session.flushes, 4)


if __name__ == "__main__":
    unittest.main()
