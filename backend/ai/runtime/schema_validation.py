class ToolSchemaValidationError(ValueError):
    pass


def validate_tool_arguments(schema: dict, arguments: dict) -> None:
    if not isinstance(arguments, dict):
        raise ToolSchemaValidationError("tool arguments must be an object")

    required = schema.get("required") or []
    for key in required:
        if key not in arguments:
            raise ToolSchemaValidationError(f"{key} is required")

    properties = schema.get("properties") or {}
    for key, value in arguments.items():
        expected = properties.get(key, {}).get("type")
        if expected is None:
            continue
        if expected == "string" and not isinstance(value, str):
            raise ToolSchemaValidationError(f"{key} must be string")
        if expected == "object" and not isinstance(value, dict):
            raise ToolSchemaValidationError(f"{key} must be object")
        if expected == "array" and not isinstance(value, list):
            raise ToolSchemaValidationError(f"{key} must be array")
        if expected == "boolean" and not isinstance(value, bool):
            raise ToolSchemaValidationError(f"{key} must be boolean")
        if expected == "integer" and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise ToolSchemaValidationError(f"{key} must be integer")
        if expected == "number" and (
            not isinstance(value, (int, float)) or isinstance(value, bool)
        ):
            raise ToolSchemaValidationError(f"{key} must be number")
