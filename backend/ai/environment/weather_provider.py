from dataclasses import asdict, dataclass
from typing import Any

import httpx


class WeatherProviderError(Exception):
    pass


class LocationRequiredError(WeatherProviderError):
    pass


class LocationNotFoundError(WeatherProviderError):
    pass


@dataclass(frozen=True)
class CurrentWeather:
    location: dict[str, Any]
    temperature_c: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None
    weather_code: int | None
    weather_description: str
    is_day: bool | None
    observed_at: str
    timezone: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


class OpenMeteoWeatherProvider:
    def __init__(
        self,
        *,
        geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search",
        forecast_url: str = "https://api.open-meteo.com/v1/forecast",
        timeout_seconds: float = 8.0,
    ):
        self._geocoding_url = geocoding_url
        self._forecast_url = forecast_url
        self._timeout_seconds = timeout_seconds

    async def get_current_weather(
        self,
        *,
        location_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> CurrentWeather:
        if location_name:
            location = await self._resolve_location(location_name)
        elif latitude is not None and longitude is not None:
            location = {
                "name": None,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": "auto",
            }
        else:
            raise LocationRequiredError("location_name or latitude/longitude is required")

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.get(
                self._forecast_url,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": ",".join(
                        [
                            "temperature_2m",
                            "apparent_temperature",
                            "precipitation",
                            "weather_code",
                            "wind_speed_10m",
                            "is_day",
                        ]
                    ),
                    "timezone": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()

        current = data.get("current") or {}
        timezone = data.get("timezone") or location.get("timezone") or "auto"
        resolved_location = {
            **location,
            "timezone": timezone,
            "latitude": data.get("latitude", location["latitude"]),
            "longitude": data.get("longitude", location["longitude"]),
        }
        return CurrentWeather(
            location=resolved_location,
            temperature_c=current.get("temperature_2m"),
            apparent_temperature_c=current.get("apparent_temperature"),
            precipitation_mm=current.get("precipitation"),
            wind_speed_kmh=current.get("wind_speed_10m"),
            weather_code=current.get("weather_code"),
            weather_description=describe_weather_code(current.get("weather_code")),
            is_day=_bool_or_none(current.get("is_day")),
            observed_at=current.get("time", ""),
            timezone=timezone,
        )

    async def _resolve_location(self, location_name: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.get(
                self._geocoding_url,
                params={
                    "name": location_name,
                    "count": 1,
                    "language": "zh",
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results") or []
        if not results:
            raise LocationNotFoundError(f"location not found: {location_name}")
        first = results[0]
        return {
            "name": first.get("name") or location_name,
            "country": first.get("country"),
            "admin1": first.get("admin1"),
            "latitude": first["latitude"],
            "longitude": first["longitude"],
            "timezone": first.get("timezone") or "auto",
        }


def describe_weather_code(code: int | None) -> str:
    descriptions = {
        0: "晴",
        1: "大致晴朗",
        2: "局部多云",
        3: "阴",
        45: "有雾",
        48: "雾凇",
        51: "小毛毛雨",
        53: "毛毛雨",
        55: "较强毛毛雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        71: "小雪",
        73: "中雪",
        75: "大雪",
        80: "小阵雨",
        81: "阵雨",
        82: "强阵雨",
        95: "雷暴",
        96: "雷暴伴小冰雹",
        99: "雷暴伴冰雹",
    }
    return descriptions.get(code, "未知天气")


def _bool_or_none(value):
    if value is None:
        return None
    return bool(value)
