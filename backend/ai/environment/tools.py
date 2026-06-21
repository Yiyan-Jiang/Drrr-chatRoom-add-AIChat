from ai.environment.time_service import (
    DEFAULT_TIMEZONE,
    current_local_time,
    day_period_label,
)
from ai.environment.weather_provider import (
    LocationNotFoundError,
    LocationRequiredError,
    OpenMeteoWeatherProvider,
    WeatherProviderError,
)
from ai.runtime.registry import ToolRegistry
from ai.runtime.results import ToolResult
from ai.runtime.tools import ToolPermission, ToolSpec


def _require_mapping(arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    return dict(arguments)


def _normalize_time(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    timezone = normalized.get("timezone") or DEFAULT_TIMEZONE
    return {"timezone": timezone}


def _normalize_weather(arguments: dict) -> dict:
    normalized = _require_mapping(arguments)
    result = {}
    location_name = normalized.get("location_name")
    if isinstance(location_name, str) and location_name.strip():
        result["location_name"] = location_name.strip()

    if "latitude" in normalized and "longitude" in normalized:
        result["latitude"] = float(normalized["latitude"])
        result["longitude"] = float(normalized["longitude"])
    return result


def register_environment_tools(
    registry: ToolRegistry,
    *,
    weather_provider=None,
    now_provider=None,
) -> None:
    provider = weather_provider or OpenMeteoWeatherProvider()

    async def time_tool(ctx, args: dict) -> ToolResult:
        payload = current_local_time(
            timezone=args.get("timezone"),
            now_provider=now_provider,
        )
        label = day_period_label(payload["day_period"])
        return ToolResult(
            tool_name="get_local_time",
            call_id=ctx.call_id,
            ok=True,
            result_kind="local_time",
            preview=(
                f"{payload['timezone']} 当前是 {payload['local_date']} "
                f"{payload['local_time']}，{label}。"
            ),
            payload=payload,
            facts=[
                {
                    "kind": "local_time",
                    "timezone": payload["timezone"],
                    "local_date": payload["local_date"],
                    "local_time": payload["local_time"],
                    "day_period": payload["day_period"],
                }
            ],
        )

    async def weather_tool(ctx, args: dict) -> ToolResult:
        if not args.get("location_name") and (
            args.get("latitude") is None or args.get("longitude") is None
        ):
            return _weather_error(
                ctx.call_id,
                "LOCATION_REQUIRED",
                "需要明确地区才能查询实时天气。",
            )

        try:
            weather = await provider.get_current_weather(
                location_name=args.get("location_name"),
                latitude=args.get("latitude"),
                longitude=args.get("longitude"),
            )
        except LocationRequiredError as exc:
            return _weather_error(ctx.call_id, "LOCATION_REQUIRED", str(exc))
        except LocationNotFoundError as exc:
            return _weather_error(ctx.call_id, "LOCATION_NOT_FOUND", str(exc))
        except WeatherProviderError as exc:
            return _weather_error(ctx.call_id, type(exc).__name__, str(exc))

        payload = weather.to_payload()
        preview = _weather_preview(payload)
        return ToolResult(
            tool_name="get_current_weather",
            call_id=ctx.call_id,
            ok=True,
            result_kind="current_weather",
            preview=preview,
            payload=payload,
            facts=[
                {
                    "kind": "current_weather",
                    "location": payload["location"],
                    "temperature_c": payload["temperature_c"],
                    "weather_description": payload["weather_description"],
                    "precipitation_mm": payload["precipitation_mm"],
                }
            ],
        )

    registry.register(
        ToolSpec(
            name="get_local_time",
            description="获取某个时区的当前本地日期和时间。",
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA 时区名，默认为 Asia/Shanghai。",
                    }
                },
            },
            permission=ToolPermission(scope="environment:read"),
            normalize=_normalize_time,
            execute=time_tool,
            when_to_use=(
                "当用户按一天的时段问候、询问当前时间/日期，"
                "或回复内容依赖早上/下午/晚上等时段语境时使用。"
            ),
        )
    )
    registry.register(
        ToolSpec(
            name="get_current_weather",
            description="获取指定地名或经纬度的真实当前天气。",
            input_schema={
                "type": "object",
                "properties": {
                    "location_name": {
                        "type": "string",
                        "description": "城市或地区名，例如 深圳 或 Tokyo。",
                    },
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
            },
            permission=ToolPermission(scope="environment:read"),
            normalize=_normalize_weather,
            execute=weather_tool,
            when_to_use=(
                "当用户询问天气、下雨、气温、风力，"
                "或提到某个具体城市/地区的当前状况时使用。"
                "如果用户没有提供地点，不要擅自猜测其所在位置。"
            ),
        )
    )


def _weather_error(call_id: str, error_code: str, message: str) -> ToolResult:
    return ToolResult(
        tool_name="get_current_weather",
        call_id=call_id,
        ok=False,
        result_kind="current_weather",
        preview=message,
        payload={},
        error_code=error_code,
        error_message=message,
    )


def _weather_preview(payload: dict) -> str:
    location = payload.get("location") or {}
    name = location.get("name") or "该地区"
    temperature = payload.get("temperature_c")
    apparent = payload.get("apparent_temperature_c")
    weather = payload.get("weather_description") or "未知天气"
    precipitation = payload.get("precipitation_mm")
    wind = payload.get("wind_speed_kmh")
    observed_at = payload.get("observed_at") or "未知时间"
    parts = [f"{name}当前{weather}"]
    if temperature is not None:
        parts.append(f"气温 {temperature}°C")
    if apparent is not None:
        parts.append(f"体感 {apparent}°C")
    if precipitation is not None:
        parts.append(f"降水 {precipitation} mm")
    if wind is not None:
        parts.append(f"风速 {wind} km/h")
    parts.append(f"更新时间 {observed_at}")
    return "，".join(parts) + "。"
