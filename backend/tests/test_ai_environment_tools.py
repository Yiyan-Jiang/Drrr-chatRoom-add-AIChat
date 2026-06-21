import unittest
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


class EnvironmentToolTest(unittest.IsolatedAsyncioTestCase):
    def _context(self):
        from ai.runtime.tools import ToolExecutionContext

        return ToolExecutionContext(
            run_id="run-1",
            session_id="session-1",
            user_id=7,
            call_id="call-1",
        )

    async def test_local_time_defaults_to_china_timezone(self):
        from ai.environment.tools import register_environment_tools
        from ai.runtime.registry import ToolRegistry

        fixed_now = datetime(2026, 6, 15, 21, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
        registry = ToolRegistry()
        register_environment_tools(registry, now_provider=lambda _timezone: fixed_now)

        result = await registry.get("get_local_time").execute(self._context(), {})

        self.assertTrue(result.ok)
        self.assertEqual(result.result_kind, "local_time")
        self.assertEqual(result.payload["timezone"], "Asia/Shanghai")
        self.assertEqual(result.payload["local_time"], "21:05")
        self.assertEqual(result.payload["day_period"], "evening")
        self.assertIn("晚上", result.preview)

    async def test_weather_requires_location_name_or_coordinates(self):
        from ai.environment.tools import register_environment_tools
        from ai.runtime.registry import ToolRegistry

        registry = ToolRegistry()
        register_environment_tools(registry, weather_provider=FakeWeatherProvider())

        result = await registry.get("get_current_weather").execute(self._context(), {})

        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "LOCATION_REQUIRED")
        self.assertIn("需要明确地区", result.preview)

    async def test_weather_uses_location_name_provider_path(self):
        from ai.environment.tools import register_environment_tools
        from ai.runtime.registry import ToolRegistry

        provider = FakeWeatherProvider()
        registry = ToolRegistry()
        register_environment_tools(registry, weather_provider=provider)

        result = await registry.get("get_current_weather").execute(
            self._context(),
            {"location_name": "深圳"},
        )

        self.assertTrue(result.ok)
        self.assertEqual(provider.location_names, ["深圳"])
        self.assertEqual(provider.coordinate_queries, [])
        self.assertEqual(result.payload["location"]["name"], "深圳")
        self.assertEqual(result.payload["temperature_c"], 28.4)
        self.assertIn("深圳", result.preview)

    async def test_weather_uses_coordinate_provider_path(self):
        from ai.environment.tools import register_environment_tools
        from ai.runtime.registry import ToolRegistry

        provider = FakeWeatherProvider()
        registry = ToolRegistry()
        register_environment_tools(registry, weather_provider=provider)

        result = await registry.get("get_current_weather").execute(
            self._context(),
            {"latitude": 22.5431, "longitude": 114.0579},
        )

        self.assertTrue(result.ok)
        self.assertEqual(provider.location_names, [])
        self.assertEqual(provider.coordinate_queries, [(22.5431, 114.0579)])
        self.assertEqual(result.payload["location"]["latitude"], 22.5431)
        self.assertEqual(result.payload["location"]["longitude"], 114.0579)


class DefaultRegistryEnvironmentToolTest(unittest.TestCase):
    def test_default_tool_registry_exposes_environment_tools(self):
        from ai.runtime.default_tools import create_default_tool_registry

        names = create_default_tool_registry().list_names()

        self.assertIn("get_local_time", names)
        self.assertIn("get_current_weather", names)


@dataclass
class FakeWeatherProvider:
    location_names: list[str] | None = None
    coordinate_queries: list[tuple[float, float]] | None = None

    def __post_init__(self):
        self.location_names = []
        self.coordinate_queries = []

    async def get_current_weather(
        self,
        *,
        location_name=None,
        latitude=None,
        longitude=None,
    ):
        from ai.environment.weather_provider import CurrentWeather

        if location_name:
            self.location_names.append(location_name)
            resolved_name = location_name
            lat = 22.5431
            lon = 114.0579
        else:
            self.coordinate_queries.append((latitude, longitude))
            resolved_name = None
            lat = latitude
            lon = longitude

        return CurrentWeather(
            location={
                "name": resolved_name,
                "latitude": lat,
                "longitude": lon,
                "timezone": "Asia/Shanghai",
            },
            temperature_c=28.4,
            apparent_temperature_c=31.2,
            precipitation_mm=0.0,
            wind_speed_kmh=11.5,
            weather_code=1,
            weather_description="多云",
            is_day=True,
            observed_at="2026-06-15T21:00",
            timezone="Asia/Shanghai",
        )


if __name__ == "__main__":
    unittest.main()
