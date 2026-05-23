from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CharacterConfig:
    default_character: str
    prompt_files: dict[str, str]


def _parse_characters_config(path: Path) -> CharacterConfig:
    default_character = "sakura"
    prompt_files: dict[str, str] = {}
    current_character: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if stripped.startswith("default_character:"):
            default_character = stripped.split(":", 1)[1].strip()
        elif indent == 2 and stripped.endswith(":"):
            current_character = stripped[:-1]
            prompt_files.setdefault(current_character, f"{current_character}.md")
        elif indent == 4 and current_character and stripped.startswith("prompt_file:"):
            prompt_files[current_character] = stripped.split(":", 1)[1].strip()

    return CharacterConfig(
        default_character=default_character,
        prompt_files=prompt_files,
    )


def _config_dir() -> Path:
    return Path(__file__).parent


def load_character_config() -> CharacterConfig:
    return _parse_characters_config(_config_dir() / "characters.yaml")


DEFAULT_CHARACTER = load_character_config().default_character


def get_allowed_characters() -> list[str]:
    return list(load_character_config().prompt_files.keys())


def normalize_character(character: str | None) -> str:
    allowed = get_allowed_characters()
    return character if character in allowed else DEFAULT_CHARACTER


def get_system_prompt(character: str = DEFAULT_CHARACTER) -> str:
    config = load_character_config()
    actual_character = normalize_character(character)
    prompt_file = config.prompt_files[actual_character]
    return (_config_dir() / prompt_file).read_text(encoding="utf-8").strip()
