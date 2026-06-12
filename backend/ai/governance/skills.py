from dataclasses import dataclass, field

from ai.ops.rollout import stable_bucket


class SkillContractError(ValueError):
    pass


@dataclass(frozen=True)
class SkillVersion:
    skill_name: str
    version: int
    tools: set[str] = field(default_factory=set)
    artifact_contracts: set[str] = field(default_factory=set)
    default: bool = False
    requires_evidence: bool = False


@dataclass(frozen=True)
class SkillRelease:
    skill_name: str
    version: int
    scope: str
    percentage: int
    user_id: int | None = None
    workspace_id: str | None = None
    status: str = "active"

    def matches(self, *, user_id: int, workspace_id: str | None) -> bool:
        if self.status != "active":
            return False
        if self.scope == "global":
            return True
        if self.scope == "workspace":
            return self.workspace_id == workspace_id
        if self.scope == "user":
            return self.user_id == user_id
        return False

    @property
    def specificity(self) -> int:
        return {"user": 3, "workspace": 2, "global": 1}.get(self.scope, 0)


def validate_skill_contract(
    skill: SkillVersion,
    *,
    known_tools: set[str],
    known_artifacts: set[str],
) -> None:
    for tool_name in skill.tools:
        if tool_name not in known_tools:
            raise SkillContractError(f"unknown tool: {tool_name}")

    for artifact_type in skill.artifact_contracts:
        if artifact_type not in known_artifacts:
            raise SkillContractError(f"unknown artifact: {artifact_type}")

    if skill.requires_evidence and "response_refs" not in skill.artifact_contracts:
        raise SkillContractError("evidence skill requires response_refs artifact")


class SkillRegistry:
    def __init__(self) -> None:
        self._versions: dict[tuple[str, int], SkillVersion] = {}
        self._releases: list[SkillRelease] = []

    def add_version(self, version: SkillVersion) -> None:
        self._versions[(version.skill_name, version.version)] = version

    def add_release(self, release: SkillRelease) -> None:
        self._releases.append(release)

    def resolve_for_run(
        self,
        skill_name: str,
        *,
        user_id: int,
        workspace_id: str | None,
    ) -> SkillVersion:
        releases = sorted(
            [release for release in self._releases if release.skill_name == skill_name],
            key=lambda release: release.specificity,
            reverse=True,
        )
        for release in releases:
            if not release.matches(user_id=user_id, workspace_id=workspace_id):
                continue
            if stable_bucket(str(user_id), skill_name) < release.percentage:
                return self._versions[(release.skill_name, release.version)]

        defaults = [
            version
            for (name, _), version in self._versions.items()
            if name == skill_name and version.default
        ]
        if not defaults:
            raise KeyError(f"default skill version not found: {skill_name}")
        return sorted(defaults, key=lambda version: version.version, reverse=True)[0]
