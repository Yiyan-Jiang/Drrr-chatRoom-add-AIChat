from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Shanghai"


def resolve_timezone(timezone: str | None = None) -> str:
    value = (timezone or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError:
        return DEFAULT_TIMEZONE
    return value


def current_local_time(
    timezone: str | None = None,
    now_provider=None,
) -> dict:
    resolved_timezone = resolve_timezone(timezone)
    now = (
        now_provider(resolved_timezone)
        if now_provider is not None
        else datetime.now(ZoneInfo(resolved_timezone))
    )
    if now.tzinfo is None:
        now = now.replace(tzinfo=ZoneInfo(resolved_timezone))
    return {
        "timezone": resolved_timezone,
        "local_date": now.strftime("%Y-%m-%d"),
        "local_time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
        "hour": now.hour,
        "day_period": day_period_for_hour(now.hour),
        "iso_datetime": now.isoformat(),
    }


def day_period_for_hour(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 18:
        return "afternoon"
    if 18 <= hour < 23:
        return "evening"
    return "night"


def day_period_label(day_period: str) -> str:
    return {
        "morning": "早上",
        "afternoon": "下午",
        "evening": "晚上",
        "night": "深夜",
    }.get(day_period, day_period)
