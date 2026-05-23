from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str


def _parse_route_config(path: Path) -> dict:
    config: dict = {"default": {}, "routes": {}}
    current_task: str | None = None
    in_characters = False
    current_character: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if not stripped.endswith(":") and ": " not in stripped:
            continue

        if stripped.endswith(":"):
            key = stripped[:-1]
            if indent == 0 and key == "routes":
                continue
            if indent == 2:
                current_task = key
                config["routes"].setdefault(current_task, {"default": {}, "characters": {}})
                in_characters = False
                current_character = None
            elif indent == 4 and key == "characters":
                in_characters = True
                current_character = None
            elif indent == 6 and in_characters and current_task:
                current_character = key
                config["routes"][current_task]["characters"].setdefault(current_character, {})
            continue

        key, value = stripped.split(": ", 1)
        value = value.strip()
        if indent == 2 and current_task is None:
            config["default"][key] = value
        elif indent == 6 and current_task and not in_characters:
            config["routes"][current_task]["default"][key] = value
        elif indent == 8 and current_task and current_character:
            config["routes"][current_task]["characters"][current_character][key] = value

    return config


def resolve_model_route(
    character: str,
    task_type: str = "chat",
    config_path: Path | None = None,
) -> ModelRoute:
    path = config_path or Path(__file__).with_name("model_routes.yaml")
    config = _parse_route_config(path)
    task_config = config["routes"].get(task_type, {})
    route = task_config.get("characters", {}).get(character)
    if route is None:
        route = task_config.get("default") or config["default"]
    return ModelRoute(provider=route["provider"], model=route["model"])
