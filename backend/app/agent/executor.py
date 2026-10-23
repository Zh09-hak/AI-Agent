import json

from backend.app.agent.tool_schemas import TOOL_SCHEMAS
from backend.app.agent.tools import TOOL_REGISTRY


def _get_schema(tool_name: str) -> dict | None:
    for schema in TOOL_SCHEMAS:
        if schema["function"]["name"] == tool_name:
            return schema["function"]
    return None


def coerce_arguments(tool_name: str, raw_args: dict) -> dict:
    schema = _get_schema(tool_name)
    if schema is None:
        return {}

    properties = schema.get("parameters", {}).get("properties", {})
    coerced: dict = {}

    for key, value in (raw_args or {}).items():
        spec = properties.get(key)
        if spec is None:
            continue

        expected = spec.get("type")
        try:
            if expected == "integer":
                coerced[key] = int(value)
            elif expected == "number":
                coerced[key] = float(value)
            elif expected == "boolean":
                coerced[key] = bool(value)
            else:
                coerced[key] = str(value)
        except (TypeError, ValueError):
            continue

    return coerced


def parse_tool_call_arguments(raw_arguments) -> dict:
    if isinstance(raw_arguments, dict):
        return raw_arguments

    if isinstance(raw_arguments, str):
        try:
            parsed = json.loads(raw_arguments)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    return {}


def execute_tool(tool_name: str, arguments: dict) -> tuple[str, str | None]:
    function = TOOL_REGISTRY.get(tool_name)
    if function is None:
        available = ", ".join(sorted(TOOL_REGISTRY.keys()))
        return "", f"Unknown tool '{tool_name}'. Available tools: {available}."

    safe_args = coerce_arguments(tool_name, arguments)

    try:
        result = function(**safe_args)
        return str(result), None
    except TypeError as exc:
        return "", f"Invalid arguments for '{tool_name}': {exc}"
    except Exception as exc:
        return "", f"Tool '{tool_name}' raised an exception: {exc}"