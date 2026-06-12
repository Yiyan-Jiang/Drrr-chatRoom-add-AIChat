from ai.skills.builtin.teaching import create_teaching_manifest
from ai.skills.manifest import SkillManifest
from ai.skills.registry import RuntimeSkillRegistry


def create_default_skill_registry(tool_registry) -> RuntimeSkillRegistry:
    return RuntimeSkillRegistry(
        [
            SkillManifest(
                name="assistant",
                version=1,
                description="General runtime assistant skill.",
                instruction="Use structured runtime tools and keep state in artifacts/checkpoints.",
                tools=["record_note"],
                artifact_contracts={"runtime_note": {"type": "object"}},
                checkpoint_schema={"type": "object"},
                policy={"allow": ["record_note"]},
            ),
            create_teaching_manifest(),
        ],
        tool_registry,
    )
