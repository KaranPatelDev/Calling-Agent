from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    return datetime.now(IST)


def is_within_calling_hours(start_hour: int, end_hour: int) -> bool:
    current_hour = now_ist().hour
    return start_hour <= current_hour < end_hour


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST).astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)
