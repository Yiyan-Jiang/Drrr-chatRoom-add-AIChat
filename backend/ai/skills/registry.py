from ai.skills.errors import SkillContractError, SkillNotFound
from ai.skills.manifest import SkillManifest


class RuntimeSkillRegistry:
    def __init__(self, manifests: list[SkillManifest], tool_registry):
        self._manifests = {(manifest.name, manifest.version): manifest for manifest in manifests}
        self._latest_by_name: dict[str, SkillManifest] = {}
        self._tool_registry = tool_registry
        for manifest in manifests:
            current = self._latest_by_name.get(manifest.name)
            if current is None or manifest.version > current.version:
                self._latest_by_name[manifest.name] = manifest

    def list_skills(self, *, user_id: int, workspace_id: str | None) -> list[dict]:
        return [
            manifest.summary()
            for manifest in sorted(
                self._latest_by_name.values(),
                key=lambda item: item.name,
            )
        ]

    def open_skill(
        self,
        name: str,
        *,
        user_id: int,
        workspace_id: str | None,
        version: int | None = None,
    ) -> SkillManifest:
        manifest = (
            self._manifests.get((name, version))
            if version is not None
            else self._latest_by_name.get(name)
        )
        if manifest is None:
            raise SkillNotFound(f"skill not found: {name}")

        try:
            manifest.validate(self._tool_registry)
        except SkillContractError:
            raise
        return manifest
